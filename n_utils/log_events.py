from __future__ import division
# Copyright 2017 Nitor Creations Oy
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

from past.utils import old_div
from botocore.exceptions import ClientError
from collections import deque
from datetime import datetime
from dateutil import tz
from termcolor import colored
from threading import Event, Thread, BoundedSemaphore
import boto3
import locale
import os
import sys
import time
import re
from botocore.config import Config
import queue
import logging


def millis2iso(millis):
    return fmttime(datetime.utcfromtimestamp(old_div(millis,1000.0)))

def timestamp(tstamp):
    return (tstamp.replace(tzinfo=None) - datetime(1970, 1, 1, tzinfo=None))\
                                                 .total_seconds() * 1000

def fmttime(tstamp):
    return tstamp.replace(tzinfo=tz.tzlocal()).isoformat()[:23]

def uprint(message):
    sys.stdout.write((message + os.linesep)\
                        .encode(locale.getpreferredencoding()))


class CloudWatchLogsThread(Thread):
    def __init__(self, log_group_name, start_time=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.log_group_name = log_group_name
        self.start_time = start_time
        self.cwlogs = CloudWatchLogsGroups(log_group_filter=self.log_group_name, start_time=self.start_time)

    def stop(self):
        self.cwlogs._stopped.set()

    def log_group_worker(self):
        cwlogs = CloudWatchLogsGroups(log_group_filter=self.log_group_name, start_time=self.start_time)
        cwlogs.get_logs()

    def run(self):
        self.cwlogs.get_logs()


class CloudWatchLogsGroups():
    def __init__(self, log_filter='', log_group_filter='', start_time=None, end_time=None, sort=False):
        self.client = boto3.client('logs')
        self.log_filter = log_filter
        self.log_group_filter = log_group_filter
        self.start_time = int(start_time) * 1000 if start_time else \
                          int((time.time() - 60) * 1000)
        self.end_time = int(end_time) * 1000 if end_time else None
        self.sort = sort
        self._stopped = Event()

    def filter_groups(self, log_group_filter, groups):
        filtered = []
        for group in groups:
            if re.search(log_group_filter, group['logGroupName']):
                filtered.append(group['logGroupName'])
        return filtered

    def get_filtered_groups(self, log_group_filter):
        resp = self.client.describe_log_groups()
        filtered_group_names = []
        filtered_group_names.extend(self.filter_groups(self.log_group_filter, resp['logGroups']))
        while resp.get('nextToken'):
            resp = self.client.describe_log_groups(nextToken=resp['nextToken'])
            filtered_group_names.extend(self.filter_groups(self.log_group_filter, resp['logGroups']))
        return filtered_group_names

    def get_logs(self):
        groups = self.get_filtered_groups(self.log_group_filter)
        print("Found log groups: %s" % (groups))
        log_threads = []
        work_queue = queue.Queue()
        semaphore = BoundedSemaphore(5)
        output_queue = queue.PriorityQueue()
        work_items = []
        for group_name in groups:
            work_item = {'item': {'logGroupName': group_name,
                                  'interleaved': True,
                                  'startTime': self.start_time,
                                  'filterPattern': self.log_filter if self.log_filter else ""
                                 },
                         'meta': {'initialQueriesDone': Event()}
                        }
            if self.end_time: work_item['item']['endTime'] = self.end_time
            work_queue.put(work_item)
            work_items.append(work_item)
        for _ in range(10):
            cwlogs_worker = CloudWatchLogsWorker(work_queue, semaphore, output_queue)
            log_threads.append(cwlogs_worker)
            cwlogs_worker.start()

        speed_limiter = SpeedLimitThread(semaphore)
        speed_limiter.start()
        all_initial_queries_done = False
        tailing = True if not self.end_time else False
        wait_time = None if self.sort else 0.0
        while not self._stopped.isSet():
            try:
                if not all_initial_queries_done:
                    loop_queries_done = True
                    for work_item in work_items:
                        if not work_item['meta']['initialQueriesDone'].wait(wait_time):
                            loop_queries_done = False
                    all_initial_queries_done = loop_queries_done
                elif self.sort: time.sleep(5.0) #allow time to sort while tailing
                while not output_queue.empty():
                    uprint(' '.join(output_queue.get()[1]))
                if all_initial_queries_done and not tailing: raise KeyboardInterrupt
            except KeyboardInterrupt:
                for thread in log_threads:
                    thread.stop()
                speed_limiter.stop()
                return

class SpeedLimitThread(Thread):
    def __init__(self, semaphore):
        Thread.__init__(self)
        self.semaphore = semaphore
        self._stopped = Event()
        self.setDaemon(True)

    def tick(self):
        while not self._stopped.wait(1.1):
            try:
                for _ in range(5): self.semaphore.release()
            except ValueError:
                pass
        return

    def stop(self):
        self._stopped.set()

    def run(self):
        self.tick()


class LogWorkerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._stopped = Event()
        self.setDaemon(True)

    def list_logs(self):
        return

    def stop(self):
        self._stopped.set()

    def run(self):
        self.list_logs()


class CloudWatchLogsWorker(LogWorkerThread):
    def __init__(self, work_queue, semaphore, output_queue):
        LogWorkerThread.__init__(self)
        self.work_queue = work_queue
        self.semaphore = semaphore
        self.output_queue = output_queue
        self.client = boto3.client('logs')

    def list_logs(self):
        do_wait = object()

        def generator():
            work_item = None
            last_timestamp = None
            while True:
                if not work_item:
                    work_item = self.work_queue.get()
                    last_timestamp = None
                self.semaphore.acquire()
                response = self.client.filter_log_events(**work_item['item'])
                for event in response.get('events', []):
                    event['logGroupName'] = work_item['item']['logGroupName']
                    last_timestamp = event.get('timestamp', None)
                    yield event

                if 'nextToken' in response:
                    work_item['item']['nextToken'] = response['nextToken']
                else:
                    if 'nextToken' in work_item['item']:
                        work_item['item'].pop('nextToken')
                    if last_timestamp:
                        work_item['item']['startTime'] = last_timestamp + 1
                    work_item['meta']['initialQueriesDone'].set()
                    self.work_queue.put(work_item)
                    work_item = None
                    yield do_wait

        for event in generator():
            if event is do_wait and not self._stopped.wait(1.0):
                continue
            elif self._stopped.is_set():
                return

            output = []
            output.append(colored(millis2iso(event['timestamp']), 'yellow'))
            output.append(colored(event['logGroupName'], 'green'))
            output.append(colored(event['logStreamName'], 'cyan'))
            output.append(event['message'])
            self.output_queue.put((event['timestamp'], output)) #sort by timestamp (first value in tuple)


class LogEventThread(Thread):

    def __init__(self, log_group_name, start_time=None, end_time=None, filter_pattern=None):
        Thread.__init__(self)
        self.log_group_name = log_group_name
        self.start_time = int(start_time) * 1000 if start_time else \
                          int((time.time() - 60) * 1000)
        self.end_time = int(end_time) * 1000 if end_time else None
        self.filter_pattern = filter_pattern
        self._stopped = Event()

    def list_logs(self):
        return

    def stop(self):
        self._stopped.set()

    def run(self):
        self.list_logs()


class CloudFormationEvents(LogEventThread):
    def __init__(self, log_group_name, start_time=None):
        LogEventThread.__init__(self, log_group_name, start_time=start_time)
        self.client = boto3.client('cloudformation')

    def list_logs(self):
        do_wait = object()
        dedup_queue = deque(maxlen=10000)
        kwargs = {'StackName': self.log_group_name}
        def generator():
            start_seen = False
            seen_events_up_to = 0
            event_timestamp = float("inf")

            while True:
                unseen_events = deque()
                response = {}
                try:
                    response = self.client.describe_stack_events(**kwargs)
                except ClientError:
                    pass
                for event in response.get('StackEvents', []):
                    event_timestamp = timestamp(event['Timestamp'])
                    if  event_timestamp < max(self.start_time,
                                              seen_events_up_to):
                        break
                    if not event['EventId'] in dedup_queue:
                        dedup_queue.append(event['EventId'])
                        unseen_events.append(event)

                if len(unseen_events) > 0:
                    seen_events_up_to = \
                        int(timestamp(unseen_events[0]['Timestamp']))
                    for event in reversed(unseen_events):
                        yield event

                # If we've seen the start, we don't want to iterate with
                # NextToken anymore
                if event_timestamp < self.start_time or \
                   'NextToken' not in response:
                    start_seen = True
                # If we've not seen the start we iterate further
                if not start_seen and 'NextToken' in response:
                    kwargs['NextToken'] = response['NextToken']
                # Otherwise make sure we don't send NextToken
                elif 'NextToken' in kwargs:
                    kwargs.pop('NextToken')
                yield do_wait

        for event in generator():
            if event is do_wait and not self._stopped.wait(1.0):
                continue
            elif self._stopped.is_set():
                return

            output = []
            output.append(colored(fmttime(event['Timestamp']),
                                  'yellow'))
            target = event['ResourceType'] + ":" + event['LogicalResourceId']
            output.append(colored(target, 'cyan'))
            message = event['ResourceStatus']
            color = 'green'
            if "_FAILED" in message:
                color = 'red'
            output.append(colored(message, color))
            if 'ResourceStatusReason' in event:
                output.append(event['ResourceStatusReason'])
            uprint(' '.join(output))
            sys.stdout.flush()
