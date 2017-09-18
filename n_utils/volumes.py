#!/usr/bin/env python

import argparse
import time
import json
import sys
import os
import subprocess
from subprocess import PIPE, Popen, CalledProcessError
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dateutil import tz
from termcolor import colored
import argcomplete
import boto3
from botocore.exceptions import ClientError
import psutil
from .cf_utils import set_region, resolve_account, InstanceInfo
from .aws_infra_util import find_include

def letter_to_target_id(letter):
    return ord(letter)-ord("f")+5

def target_id_to_letter(target_id):
    return str(unichr(target_id-5+ord("f")))

def wmic_partition_get():
    return wmic_get("partition")

def wmic_diskdrive_get():
    return wmic_get("diskdrive")

def wmic_volume_get():
    return wmic_get("volume")

def wmic_get(command):
    ret = []
    proc = Popen(["wmic", command, "get",
                  "/format:rawxml"], stdout=PIPE, stderr=PIPE)
    output = proc.communicate()[0]
    tree = ET.fromstring(output)
    for elem in tree.iter("RESULTS"):
        for inst in elem.iter("INSTANCE"):
            disk = {}
            for prop in inst.iter("PROPERTY"):
                try:
                    disk[prop.attrib['NAME']] = int(prop.findtext("*"))
                except ValueError:
                    disk[prop.attrib['NAME']] = prop.findtext("*")
                except TypeError:
                    continue
            ret.append(disk)
    return ret

def wmic_disk_with_target_id(target_id):
    return [x for x in wmic_diskdrive_get() if x['SCSITargetId'] == target_id][0]

def wmic_max_target_id():
    return sorted([x['SCSITargetId'] for x in wmic_diskdrive_get()],
                  reverse=True)[0]

def disk_by_drive_letter(drive_letter):
    ret = {}
    proc = Popen(["powershell.exe", find_include("disk-by-drive-letter.ps1"),
                  drive_letter.upper() + ":"], stdout=PIPE, stderr=PIPE)
    output = proc.communicate()[0]
    tree = ET.fromstring(output)
    for obj in tree.iter("Object"):
        for prop in obj.iter("Property"):
            try:
                ret[prop.attrib['Name']] = int(prop.findtext("."))
            except ValueError:
                ret[prop.attrib['Name']] = prop.findtext(".")
            except TypeError:
                continue
    return ret

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
                         size_gb=None, del_on_termination=True):
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
    if del_on_termination:
        delete_on_termination(device)
    if not snapshot:
        #empty device
        if sys.platform.startswith('win'):
            #Windows format
            disk = wmic_disk_with_target_id(letter_to_target_id(device[-1:]))
            drive_letter = mount_path[0].upper()
            disk_number = str(disk['Index'])
            subprocess.check_call(["powershell.exe", "Get-Disk", disk_number,
                                   "|", "Set-Disk", "-IsOffline", "$False"])
            subprocess.check_call(["powershell.exe", "Initialize-Disk",
                                   disk_number, "-PartitionStyle", "MBR"])
            subprocess.check_call(["powershell.exe", "New-Partition",
                                   "-DiskNumber", disk_number,
                                   "-UseMaximumSize", "-DriveLetter",
                                   drive_letter])
            print "Formatting " + device + "(" + drive_letter + ":)"
            subprocess.check_call(["powershell.exe", "Format-Volume",
                                   "-DriveLetter", drive_letter, "-FileSystem",
                                   "NTFS", "-Force", "-Confirm:$False"])
        else:
            #linux format
            print "Formatting " + device
            subprocess.check_call(["mkfs.ext4", device])
    else:
        if sys.platform.startswith('win'):
            target_id = letter_to_target_id(device[-1:])
            disk = wmic_disk_with_target_id(target_id)
            drive_letter = mount_path[0].upper()
            disk_number = str(disk['Index'])
            with open(os.devnull, 'w') as devnull:
                subprocess.call(["powershell.exe", "Initialize-Disk",
                                 disk_number, "-PartitionStyle", "MBR"],
                                stderr=devnull, stdout=devnull)
            subprocess.check_call(["powershell.exe", "Get-Disk", disk_number,
                                   "|", "Set-Disk", "-IsOffline", "$False"])
            with open(os.devnull, 'w') as devnull:
                subprocess.check_call(["powershell.exe", "Get-Partition",
                                       "-DiskNumber", disk_number,
                                       "-PartitionNumber", "1"
                                       "|", "Set-Partition", "-NewDriveLetter",
                                       drive_letter], stdout=devnull,
                                      stderr=devnull)
            #resize win partition if necessary
            if size_gb and not size_gb == snapshot.volume_size:
                proc = subprocess.Popen(["powershell.exe",
                                         "$((Get-PartitionSupportedSize -Dri" +\
                                         "veLetter " + drive_letter + \
                                         ").SizeMax)"],
                                        stdout=subprocess.PIPE)
                max_size = proc.communicate()[0]
                subprocess.check_call(["powershell.exe", "Resize-Partition",
                                       "-DriveLetter", drive_letter, "-Size",
                                       max_size])
        else:
            if size_gb and not size_gb == snapshot.volume_size:
                print "Resizing " + device + " from " + \
                       str(snapshot.volume_size) + "GB to " + str(size_gb)
                try:
                    subprocess.check_call(["e2fsck", "-f", "-p", device])
                except CalledProcessError as e:
                    print "Filesystem check returned " + str(e.returncode)
                    if e.returncode > 1:
                        raise Exception("Uncorrected filesystem errors - please fix manually")
                subprocess.check_call(["resize2fs", device])
    if not sys.platform.startswith('win'):
        if not os.path.isdir(mount_path):
            os.makedirs(mount_path)
        subprocess.check_call(["mount", device, mount_path])


def first_free_device():
    if sys.platform.startswith('win'):
        max_target = wmic_max_target_id()
        if max_target == 0:
            return "/dev/xvdf"
        else:
            return "/dev/xvd" + target_id_to_letter(max_target + 1)
    else:
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
        resp = ec2.describe_volumes(VolumeIds=[volume_id])
        if "Volumes" in resp:
            volume = resp['Volumes'][0]

def match_volume_state(volume, status):
    if not volume:
        return False
    if status == "attached":
        return 'Attachments' in volume and len(volume['Attachments']) > 0 and \
               volume['Attachments'][0]['State'] == "attached"
    else:
        return volume['State'] == status

def wait_for_snapshot_complete(snapshot_id, timeout_sec=900):
    set_region()
    start = time.time()
    ec2 = boto3.client("ec2")
    snapshot = None
    while not is_snapshot_complete(snapshot):
        time.sleep(2)
        if time.time() - start > timeout_sec:
            raise Exception("Failed waiting for status 'completed' for " +\
                            snapshot_id + " (timeout: " + str(timeout_sec) + ")")
        resp = ec2.describe_snapshots(SnapshotIds=[snapshot_id])
        if "Snapshots" in resp:
            snapshot = resp['Snapshots'][0]

def is_snapshot_complete(snapshot):
    return snapshot is not None and 'State' in snapshot and \
           snapshot['State'] == 'completed'

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

def detach_volume(mount_path):
    set_region()
    device = device_from_mount_path(mount_path)
    ec2 = boto3.client("ec2")
    instance_id = InstanceInfo().instance_id()
    volume = ec2.describe_volumes(Filters=[{"Name": "attachment.device",
                                            "Values": [device]},
                                           {"Name": "attachment.instance-id",
                                            "Values": [instance_id]}])
    volume_id = volume['Volumes'][0]['VolumeId']
    ec2.detach_volume(VolumeId=volume_id, InstanceId=instance_id)

# Usage: create_snapshot volume_id tag_key tag_value
def create_snapshot(tag_key, tag_value, mount_path, wait=False):
    set_region()
    device = device_from_mount_path(mount_path)
    with open(os.devnull, 'w') as devnull:
        subprocess.call(["sync", mount_path[0]], stdout=devnull,
                        stderr=devnull)
    ec2 = boto3.client("ec2")
    instance_id = InstanceInfo().instance_id()
    volume = ec2.describe_volumes(Filters=[{"Name": "attachment.device",
                                            "Values": [device]},
                                           {"Name": "attachment.instance-id",
                                            "Values": [instance_id]}])
    volume_id = volume['Volumes'][0]['VolumeId']
    snap = ec2.create_snapshot(VolumeId=volume_id)
    ec2.create_tags(Resources=[snap['SnapshotId']],
                    Tags=[{'Key': tag_key, 'Value': tag_value},
                          {'Key': 'Name', 'Value': tag_value}])
    if wait:
        wait_for_snapshot_complete(snap['SnapshotId'])
    return snap['SnapshotId']

def device_from_mount_path(mount_path):
    if sys.platform.startswith('win'):
        return "/dev/xvd" + \
                 target_id_to_letter(disk_by_drive_letter(
                     mount_path[0])['TargetId'])
    else:
        return [x for x in psutil.disk_partitions() \
                      if x.mountpoint == mount_path][0].device

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
                    time.sleep(0.2)
                except ClientError as err:
                    print colored("Delete failed: " + \
                                  err.response['Error']['Message'], "red")
            else:
                print colored("Skipping " + snapshot['SnapshotId'], "cyan") +\
                              " || " + \
                              time.strftime("%a, %d %b %Y %H:%M:%S",
                                            print_time) +\
                              " || " + json.dumps(tags)
