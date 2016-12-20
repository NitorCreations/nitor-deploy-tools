#!/usr/bin/env python

# Copyright 2016 Nitor Creations Oy
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
import boto3
import time
import os
import json
import requests
from requests.exceptions import ConnectionError

class InstanceInfo(object):
    _info = None
    stackName = ""
    stackId = ""
    instanceId = ""
    initialStatus = ""
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
                self.instanceId = self._info['instanceId']
                os.environ['AWS_DEFAULT_REGION'] = self._info['region']
                ec2 = boto3.client('ec2')
                tags = {}
                tagResponse = ec2.describe_tags(Filters=
                                                [{'Name': 'resource-id',
                                                  'Values': [self.instanceId]}])
                for tag in tagResponse['Tags']:
                    tags[tag['Key']] = tag['Value']
                self._info['Tags'] = tags
                if 'aws:cloudformation:stack-name' in self._info['Tags']:
                    self.stackName = tags['aws:cloudformation:stack-name']
                if 'aws:cloudformation:stack-id' in self._info['Tags']:
                    self.stackId = tags['aws:cloudformation:stack-id']
                if self.stackName:
                    clf = boto3.client('cloudformation')
                    stacks = clf.describe_stacks(StackName=self.stackName)
                    stackParameters = {}
                    for parameter in stacks['Stacks'][0]['Parameters']:
                        stackParameters[parameter['ParameterKey']] = parameter['ParameterValue']
                    for output in  stacks['Stacks'][0]['Outputs']:
                        stackParameters[output['OutputKey']] = output['OutputValue']
                    self._info['StackData'] = stackParameters
            except ConnectionError:
                self._info = {}
            infoFile = None
            if os.path.isdir('C:/'):
                if not os.path.isdir('C:/nitor'):
                    os.makedirs('C:/nitor')
                infoFile = 'C:/nitor/instance-data.json'
            elif not os.path.isdir('/opt/nitor'):
                os.makedirs('/opt/nitor')
           if os.path.isdir('/opt/nitor'):
                infoFile = '/opt/nitor/instance-data.json'
            with open(infoFile, 'w') as outf:
                outf.write(json.dumps(self._info))
       if 'instanceId' in self._info:
               self.instanceId = self._info['instanceId']
       if 'region' in self._info:
               os.environ['AWS_DEFAULT_REGION'] = self._info['region']
        if 'FullStackData' in self._info and 'StackStatus' in self._info['FullStackData']:
            self.initialStatus = self._info['FullStackData']['StackStatus']
        if 'Tags' in self._info:
            if 'aws:cloudformation:stack-name' in self._info['Tags']:
                self.stackName = tags['aws:cloudformation:stack-name']
            if 'aws:cloudformation:stack-id' in self._info['Tags']:
                self.stackId = tags['aws:cloudformation:stack-id']
    def stackData(self, name):
        if 'StackData' in self._info:
            if name in self._info['StackData']:
                return self._info['StackData'][name]
        return ''

class LogSender(object):
    def __init__(self, fileName):
        info = InstanceInfo()
        self._logs = boto3.client('logs')
        self.groupName = "instanceDeployment"
        self.streamName = info.stackName + "/" + info.instanceId + "/" + fileName
        try:
            self._logs.create_log_group(logGroupName=self.groupName)
        except:
            pass
        try:
            self._logs.create_log_stream(logGroupName=self.groupName,
                                         logStreamName=self.streamName)
        except:
            pass
        streamDesc = self._logs.describe_log_streams(logGroupName=self.groupName,
                                                     logStreamNamePrefix=self.streamName)
        self.token = None
        if 'uploadSequenceToken' in streamDesc['logStreams'][0]:
            self.token = streamDesc['logStreams'][0]['uploadSequenceToken']
    def send(self, line):
        events = []
       message = line.decode('utf-8','ignore').rstrip()
        event = {}
        event['timestamp'] = int(time.time() * 1000)
        event['message'] = message
        events.append(event)
        if self.token:
            logResponse = self._logs.put_log_events(logGroupName=self.groupName,
                                                    logStreamName=self.streamName,
                                                    logEvents=events,
                                                    sequenceToken=self.token)
        else:
            logResponse = self._logs.put_log_events(logGroupName=self.groupName,
                                                    logStreamName=self.streamName,
                                                    logEvents=events)
        if 'CLOUDWATCH_LOG_DEBUG' in os.environ:
            print "Sent " + message + " to " + self.streamName
        self.token = logResponse['nextSequenceToken']

def send_logs_to_cloudwatch(fileName):
    logSender = LogSender(fileName)
    read_and_follow(fileName, logSender.send)

def read_and_follow(fileName, lineFunction, s=1):
    with open(fileName) as file_:
        endSeen = False
        while True:
            curr_position = file_.tell()
            line = file_.readline()
            if not line:
                file_.seek(curr_position)
                endSeen = True
            else:
                lineFunction(line)
                endSeen = False
            if endSeen:
                time.sleep(s)
