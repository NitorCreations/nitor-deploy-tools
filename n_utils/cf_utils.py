#!/usr/bin/env python

# Copyright 2016-2017 Nitor Creations Oy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Utilities to work with instances made by nitor-deploy-tools stacks
"""
import json
import os
import random
import requests
import stat
import string
import time
from threading import Event, Lock, Thread

import boto3
from botocore.exceptions import ClientError
from collections import deque
from datetime import datetime, timedelta
from dateutil import tz
from requests.exceptions import ConnectionError
from termcolor import colored


class InstanceInfo(object):
    """ A class to get the relevant metadata for an instance running in EC2
        firstly from the metadata service and then from EC2 tags and then
        from the CloudFormation template that created this instance

        The info is then cached in /opt/nitor/instance-data.json on linux and
        in  C:\\nitor\\instance-data.json on windows.
    """
    _info = None
    stack_name = ""
    stack_id = ""
    instance_id = ""
    region = ""
    initial_status = ""
    logical_id = ""
    def __init__(self):
        if os.path.isfile('/opt/nitor/instance-data.json'):
            try:
                self._info = json.loads(open('/opt/nitor/instance-data.json'))
            except:
                pass
        if os.path.isfile('C:/nitor/instance-data.json'):
            try:
                self._info = json.loads(open('C:/nitor/instance-data.json'))
            except:
                pass
        if not self._info:
            try:
                response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
                self._info = json.loads(response.text)
                self.instance_id = self._info['instanceId']
                self.region = self._info['region']
                os.environ['AWS_DEFAULT_REGION'] = self.region
                ec2 = boto3.client('ec2')
                tags = {}
                tag_response = ec2.describe_tags(Filters=
                                                 [{'Name': 'resource-id',
                                                   'Values': [self.instance_id]}])
                for tag in tag_response['Tags']:
                    tags[tag['Key']] = tag['Value']
                self._info['Tags'] = tags
                if 'aws:cloudformation:stack-name' in self._info['Tags']:
                    self.stack_name = tags['aws:cloudformation:stack-name']
                if 'aws:cloudformation:stack-id' in self._info['Tags']:
                    self.stack_id = tags['aws:cloudformation:stack-id']
                if self.stack_name:
                    clf = boto3.client('cloudformation')
                    stacks = clf.describe_stacks(StackName=self.stack_name)
                    stack = stacks['Stacks'][0]
                    if 'CreationTime' in stack:
                        stack['CreationTime'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                                              stack['CreationTime'].timetuple())
                    if 'LastUpdatedTime' in stack:
                        stack['LastUpdatedTime'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                                                 stack['LastUpdatedTime'].timetuple())
                    stack_parameters = {}
                    if 'Parameters' in stack:
                        for parameter in stack['Parameters']:
                            stack_parameters[parameter['ParameterKey']] = parameter['ParameterValue']
                    if 'Outputs' in stack:
                        for output in stack['Outputs']:
                            stack_parameters[output['OutputKey']] = output['OutputValue']
                    self._info['StackData'] = stack_parameters
                    self._info['FullStackData'] = stacks['Stacks'][0]
            except ConnectionError:
                self._info = {}
            info_file = None
            info_file_dir = None
            if os.path.isdir('C:/'):
                info_file_dir = 'C:/nitor'
            else:
                info_file_dir = '/opt/nitor'
            if not os.path.isdir(info_file_dir):
                os.makedirs(info_file_dir)
            info_file = info_file_dir + '/instance-data.json'
            with open(info_file, 'w') as outf:
                outf.write(json.dumps(self._info, skipkeys=True, indent=2))
            try:
                os.chmod(info_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP |
                         stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
                os.chmod(info_file_dir, stat.S_IRUSR | stat.S_IWUSR |
                         stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP |
                         stat.S_IXGRP | stat.S_IROTH | stat.S_IWOTH |
                         stat.S_IXOTH)
            except:
                print "Unable to change mode for " + info_file
        if 'instance_id' in self._info:
            self.instance_id = self._info['instance_id']
        if 'region' in self._info:
            self.region = self._info['region']
            os.environ['AWS_DEFAULT_REGION'] = self.region
        if 'FullStackData' in self._info and 'StackStatus' in self._info['FullStackData']:
            self.initial_status = self._info['FullStackData']['StackStatus']
        if 'Tags' in self._info:
            tags = self._info['Tags']
            if 'aws:cloudformation:stack-name' in tags:
                self.stack_name = tags['aws:cloudformation:stack-name']
            if 'aws:cloudformation:stack-id' in tags:
                self.stack_id = tags['aws:cloudformation:stack-id']
            if 'aws:cloudformation:logical-id' in tags:
                self.logical_id = tags['aws:cloudformation:logical-id']
    def stack_data(self, name):
        if 'StackData' in self._info:
            if name in self._info['StackData']:
                return self._info['StackData'][name]
        return ''
    def __str__(self):
        return json.dumps(self._info, skipkeys=True)

class IntervalThread(Thread):
    def __init__(self, event, interval, call_function):
        Thread.__init__(self)
        self._stopped = event
        self._interval = interval
        self._call_function = call_function

    def run(self):
        while not self._stopped.wait(self._interval):
            self._call_function()

class LogSender(object):
    def __init__(self, file_name):
        info = InstanceInfo()
        self._lock = Lock()
        self._send_lock = Lock()
        self._logs = boto3.client('logs')
        self.group_name = info.stack_name
        self._messages = deque()
        self.stream_name = info.instance_id + "|" + \
                           file_name.replace(':', '_').replace('*', '_')
        try:
            self._logs.create_log_group(logGroupName=self.group_name)
        except:
            pass
        try:
            self._logs.create_log_stream(logGroupName=self.group_name,
                                         logStreamName=self.stream_name)
        except:
            pass
        self.token = None
        self.send(str(info))
        self._do_send()
        self._stop_flag = Event()
        self._thread = IntervalThread(self._stop_flag, 2, self._do_send)
        self._thread.start()

    def send(self, line):
        try:
            self._lock.acquire()
            self._messages.append(line.decode('utf-8', 'replace').rstrip())
            if 'CLOUDWATCH_LOG_DEBUG' in os.environ:
                print "Queued message"
        finally:
            self._lock.release()

    def _do_send(self):
        events = []
        try:
            self._lock.acquire()
            if len(self._messages) == 0:
                return
            counter = 0
            while len(self._messages) > 0 and counter < 1048576 and \
                  len(events) < 10000:
                message = self._messages.popleft()
                counter = counter + len(message.encode('utf-8', 'replace')) + 26
                if counter > 1048576:
                    self._messages.appendleft(message)
                elif message:
                    event = {}
                    event['timestamp'] = int(time.time() * 1000)
                    event['message'] = message
                    events.append(event)
        finally:
            self._lock.release()
        if len(events) == 0:
            return
        try:
            self._send_lock.acquire()
            if not self.token:
                stream_desc = self._logs.describe_log_streams(logGroupName=self.group_name,
                                                              logStreamNamePrefix=self.stream_name)
                if 'uploadSequenceToken' in stream_desc['logStreams'][0]:
                    self.token = stream_desc['logStreams'][0]['uploadSequenceToken']
            if self.token:
                log_response = self._logs.put_log_events(logGroupName=self.group_name,
                                                         logStreamName=self.stream_name,
                                                         logEvents=events,
                                                         sequenceToken=self.token)
            else:
                log_response = self._logs.put_log_events(logGroupName=self.group_name,
                                                         logStreamName=self.stream_name,
                                                         logEvents=events)
            if 'CLOUDWATCH_LOG_DEBUG' in os.environ:
                print "Sent " + str(len(events)) + " messages to " + self.stream_name
            self.token = log_response['nextSequenceToken']
        except ClientError:
            self.token = None
            for event in events:
                self.send(event['message'].encode('utf-8', 'replace'))
        finally:
            self._send_lock.release()

def send_logs_to_cloudwatch(file_name):
    log_sender = LogSender(file_name)
    read_and_follow(file_name, log_sender.send)

def read_and_follow(file_name, line_function, wait=1):
    while not os.path.isfile(file_name):
        time.sleep(wait)
    with open(file_name) as file_:
        end_seen = False
        while True:
            curr_position = file_.tell()
            line = file_.readline()
            if not line:
                file_.seek(curr_position)
                end_seen = True
            else:
                line_function(line)
                end_seen = False
            if end_seen:
                time.sleep(wait)

def signal_status(status, resource_name=None):
    info = InstanceInfo()
    clf = boto3.client('cloudformation')
    if not resource_name:
        resource_name = info.logical_id
    print "Signalling " + status + " for " + info.stack_name + "." +\
          resource_name
    clf.signal_resource(StackName=info.stack_name,
                        LogicalResourceId=resource_name,
                        UniqueId=info.instance_id,
                        Status=status)

def associate_eip(eip=None, allocation_id=None, eip_param="paramEip",
                  allocation_id_param="paramEipAllocationId"):
    if not eip_param:
        eip_param = "paramEip"
    if not allocation_id_param:
        allocation_id_param="paramEipAllocationId"
    info = InstanceInfo()
    if not allocation_id:
        if eip:
            ec2 = boto3.client('ec2')
            address_data = ec2.describe_addresses(PublicIps=[eip])
            if 'Addresses' in address_data and \
               len(address_data['Addresses']) > 0 and \
               'AllocationId' in address_data['Addresses'][0]:
                allocation_id = address_data['Addresses'][0]['AllocationId']
    if not allocation_id:
        allocation_id = info.stack_data(allocation_id_param)
    if not allocation_id:
        eip = info.stack_data(eip_param)
        ec2 = boto3.client('ec2')
        address_data = ec2.describe_addresses(PublicIps=[eip])
        if 'Addresses' in address_data and len(address_data['Addresses']) > 0 \
           and 'AllocationId' in address_data['Addresses'][0]:
            allocation_id = address_data['Addresses'][0]['AllocationId']
    print "Allocating " + allocation_id + " on " + info.instance_id
    ec2 = boto3.client('ec2')
    ec2.associate_address(InstanceId=info.instance_id,
                          AllocationId=allocation_id,
                          AllowReassociation=True)

def init():
    info = InstanceInfo()
    return str(info)

def get_userdata(outfile):
    response = requests.get('http://169.254.169.254/latest/user-data')
    if outfile == "-":
        print response.text
    else:
        with open(outfile, 'w') as outf:
            outf.write(response.text)
def id_generator(size=10, chars=string.ascii_uppercase + string.digits + \
                 string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

def assume_role(role_arn):
    sts = boto3.client("sts")
    response = sts.assume_role(RoleArn=role_arn, RoleSessionName="n-sess-" + \
                               id_generator())
    return response['Credentials']

def resolve_account():
    try:
        response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
        instance_data = json.loads(response.text)
        account_id = instance_data['accountId']
        if 'AWS_DEFAULT_REGION' not in os.environ:
            os.environ['AWS_DEFAULT_REGION'] = instance_data['region']
    except ConnectionError:
        iam = boto3.client("iam")
        arn = iam.get_user()['User']['Arn']
        account_id = arn.split(':')[4]
    return account_id

def clean_snapshots(days, tags):
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
