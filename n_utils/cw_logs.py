import sys
import time
import locale
import codecs
from threading import Event, Thread
from datetime import datetime
from collections import deque
import boto3
from botocore.exceptions import ClientError
from termcolor import colored

def millis2iso(millis):
    res = datetime.utcfromtimestamp(millis/1000.0).isoformat()
    return (res + ".000")[:23] + 'Z'

class CloudWatchLogs(Thread):

    def __init__(self, log_group_name, start_time=None):
        Thread.__init__(self)
        self.log_group_name = log_group_name
        self.start_time = long(start_time) * 1000 if start_time else long((time.time() - 60) * 1000)
        self.client = boto3.client('logs')
        self._stopped = Event()

    def list_logs(self):
        if sys.version_info < (3, 0):
            sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
        do_wait = object()
        interleaving_sanity = deque(maxlen=10000)

        def generator():
            streams = list(self.get_streams())
            while True:
                if len(streams) > 0:
                    kwargs = {'logGroupName': self.log_group_name,
                              'interleaved': True, 'logStreamNames': streams,
                              'startTime': self.start_time}
                    response = self.client.filter_log_events(**kwargs)
                    for event in response.get('events', []):
                        if event['eventId'] not in interleaving_sanity:
                            interleaving_sanity.append(event['eventId'])
                            yield event

                    if 'nextToken' in response:
                        kwargs['nextToken'] = response['nextToken']
                    else:
                        streams = list(self.get_streams())
                        if 'nextToken' in kwargs:
                            kwargs.pop('nextToken')
                        yield do_wait
                else:
                    streams = list(self.get_streams())
                    yield do_wait


        for event in generator():
            if event is do_wait and not self._stopped.wait(1.0):
                continue
            elif self._stopped.is_set():
                return

            output = []
            output.append(colored(millis2iso(event['timestamp']), 'yellow'))
            output.append(colored(event['logStreamName'], 'cyan'))
            output.append(event['message'])
            print ' '.join(output)
            sys.stdout.flush()

    def get_streams(self):
        """Returns available CloudWatch logs streams in for stack"""
        kwargs = {'logGroupName': self.log_group_name}
        paginator = self.client.get_paginator('describe_log_streams')
        try:
            for page in paginator.paginate(**kwargs):
                for stream in page.get('logStreams', []):
                    if stream['lastEventTimestamp'] > self.start_time:
                        yield stream['logStreamName']
        except ClientError as err:
            return

    def stop(self):
        self._stopped.set()

    def run(self):
        self.list_logs()
