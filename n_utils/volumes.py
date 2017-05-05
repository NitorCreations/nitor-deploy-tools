.#!/usr/bin/env python

import argparse
import time
import json
import sys
import os
import subprocess
from datetime import datetime, timedelta
from dateutil import tz
from termcolor import colored
import argcomplete
import boto3
from botocore.exceptions import ClientError
import psutil
from .cf_utils import set_region, resolve_account, InstanceInfo

def latest_snapshot():
    """Get the latest snapshot with a given tag
    """
    parser = argparse.ArgumentParser(description=latest_snapshot.__doc__)
    parser.add_argument("tag", help="The tag to find snapshots with")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    print first_free_device()
    snapshot = get_latest_snapshot(args.tag, args.tag)
    if snapshot:
        print snapshot.id
    else:
        sys.exit(1)

def volume_from_snapshot(tag_key, tag_value, mount_path, availability_zone=None,
                         size_gb=None):
    set_region()
    snapshot = get_latest_snapshot(tag_key, tag_value)
    if snapshot:
        print "Found snapshot " + snapshot.id
        volume = create_volume(snapshot.id, availability_zone=availability_zone,
                               size_gb=size_gb)
    else:
        if not size_gb:
            size_gb = 32
        print "Creating empty volyme of size " + str(size_gb)
        volume = create_empty_volume(size_gb,
                                     availability_zone=availability_zone)
    device = first_free_device()
    print "Attaching volume " + volume + " to " + device
    attach_volume(volume, device)
    if not snapshot:
        #empty device
        if sys.platform.startswith('win'):
            #format win disk_partition
            import windll
            from ctypes import *

            def myFmtCallback(command, modifier, arg):
                print "FmtCallback: " + str(command)
                return 1
            
            def format_drive(Drive, Format, Title):
                fm = windll.LoadLibrary('fmifs.dll')
                FMT_CB_FUNC = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
                FMIFS_UNKNOWN = 0
                fm.FormatEx(c_wchar_p(Drive), FMIFS_UNKNOWN, c_wchar_p(Format),
                            c_wchar_p(Title), True, c_int(0),
                            FMT_CB_FUNC(myFmtCallback))
            print "Formatting Z:\\ as NTFS"
            format_drive("Z:\\", "NTFS", "EBS")
        else:
            #linux format
            print "Formatting " + device
            subprocess.check_call(["mkfs.ext4", device])
    else:
        if sys.platform.startswith('win'):
            #resize win partition if necessary
            print "win"
        else:
            if size_gb and not size_gb == snapshot.volume_size:
                print "Resizing " + device + " from " + snapshot.volume_size +\
                      "GB to " + size_gb
                subprocess.check_call(["e2fsck", "-f", "-p", device])
                subprocess.check_call(["resize2fs",  device])
            

def first_free_device():
    devices = [x.device for x in psutil.disk_partitions()]
    print devices
    for letter in "fghijklmnopqrstuvxyz":
        device = "/dev/xvd" + letter
        if device not in devices and not os.path.exists(device):
            return device
    return None

def get_latest_snapshot(tag_name, tag_value):
    """Get the latest snapshot with a given tag
    """
    set_region()
    ec2res = boto3.resource("ec2")
    snapshots = sorted(ec2res.snapshots.filter(
        Filters=[{'Name': 'tag:' + tag_name,
                  'Values': [tag_value]}]),
                       key=lambda k: k.start_time, reverse=True)
    if snapshots:
        return snapshots[0]
    else:
        return None

# Usage: create_volume snapshot-id [size_gb]
def create_volume(snapshot_id, availability_zone=None, size_gb=None):
    set_region()
    ec2 = boto3.client("ec2")
    args = {'SnapshotId': snapshot_id,
            'VolumeType': 'gp2'}
    if not availability_zone:
        availability_zone = InstanceInfo().availability_zone()
    args['AvailabilityZone'] = availability_zone
    if size_gb:
        args['Size'] = size_gb
    resp = ec2.create_volume(**args)
    wait_for_volume_status(resp['VolumeId'], "available")
    return resp['VolumeId']

# Usage: create_empty_volume size_gb
def create_empty_volume(size_gb, availability_zone=None):
    set_region()
    ec2 = boto3.client("ec2")
    args = {'Size': size_gb,
            'VolumeType': 'gp2'}
    if not availability_zone:
        availability_zone = InstanceInfo().availability_zone()
    args['AvailabilityZone'] = availability_zone
    resp = ec2.create_volume(**args)
    wait_for_volume_status(resp['VolumeId'], "available")
    return resp['VolumeId']

def wait_for_volume_status(volume_id, status, timeout_sec=300):
    set_region()
    start = time.time()
    ec2 = boto3.client("ec2")
    volume = None
    while not match_volume_state(volume, status):
        time.sleep(2)
        if time.time() - start > timeout_sec:
            raise Exception("Failed waiting for status '" + status + "' for " +\
                            volume_id + " (timeout: " + str(timeout_sec) + ")")
        volume = ec2.describe_volumes(VolumeIds=[volume_id]).Volumes[0]

def match_volume_state(volume, status):
    if not volume:
        return False
    if status == "attached":
        return 'Attachments' in volume and len(volume['Attachments']) > 0 and \
               volume['Attachments'][0]['State'] == "attached"
    else:
        return volume['State'] == status

# Usage: attach_volume volume-id device-path
def attach_volume(volume_id, device_path):
    set_region()
    ec2 = boto3.client("ec2")
    instance_id = InstanceInfo().instance_id()
    ec2.attach_volume(VolumeId=volume_id, InstanceId=instance_id,
                      Device=device_path)
    wait_for_volume_status(volume_id, "attached")

# Usage: delete_on_termination device-path
def delete_on_termination(device_path):
    set_region()
    ec2 = boto3.client("ec2")
    instance_id = InstanceInfo().instance_id()
    ec2.modify_instance_attribute(InstanceId=instance_id,
                                  BlockDeviceMappings=[{
                                      "DeviceName": device_path,
                                      "Ebs":{"DeleteOnTermination": True}}])

# Usage: create_snapshot volume_id tag_key tag_value
def create_snapshot(volume_id, tag_key, tag_value):
    set_region()
    ec2 = boto3.client("ec2")
    snap = ec2.create_snapshot(VolumeId=volume_id)
    ec2.create_tags(Resources=[snap['SnapshotId']],
                    Tags=[{'Key': tag_key, 'Value': tag_value}])

def clean_snapshots(days, tags):
    set_region()
    ec2 = boto3.client("ec2")
    account_id = resolve_account()
    newest_timestamp = datetime.utcnow() - timedelta(days=days)
    newest_timestamp = newest_timestamp .replace(tzinfo=None)
    paginator = ec2.get_paginator('describe_snapshots')
    for page in paginator.paginate(OwnerIds=[account_id],
                                   Filters=[{'Name': 'tag-value',
                                             'Values': tags}],
                                   PaginationConfig={'PageSize': 1000}):
        for snapshot in page['Snapshots']:
            tags = {}
            for tag in snapshot['Tags']:
                tags[tag['Key']] = tag['Value']
            print_time = snapshot['StartTime'].replace(tzinfo=\
                                                       tz.tzlocal()).timetuple()
            compare_time = snapshot['StartTime'].replace(tzinfo=None)
            if compare_time < newest_timestamp:
                print colored("Deleting " + snapshot['SnapshotId'], "yellow") +\
                              " || " +\
                              time.strftime("%a, %d %b %Y %H:%M:%S",
                                            print_time) + \
                              " || " + json.dumps(tags)
                try:
                    ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                except ClientError as err:
                    print colored("Delete failed: " + \
                                  err.response['Error']['Message'], "red")
            else:
                print colored("Skipping " + snapshot['SnapshotId'], "cyan") +\
                              " || " + \
                              time.strftime("%a, %d %b %Y %H:%M:%S",
                                            print_time) +\
                              " || " + json.dumps(tags)
