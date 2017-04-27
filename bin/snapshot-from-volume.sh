#!/bin/bash

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
if [ "$_ARGCOMPLETE" ]; then
  # Handle command completion executions
  exit 0
fi

PATH=$PATH:/usr/local/bin:/usr/bin:/bin

source $(n-include ebs-functions.sh)

# Usage fail message
fail() {
  echo $1
  exit 1
}
if [ "$1" = "-w" ]; then
  WAIT=1
  shift
  if [[ "$1" =~ ^[[:digit:]]*$ ]]; then
    WAIT_TIME=$1
    shift
  else
    WAIT_TIME=300
  fi
fi
set_region
SNAPSHOT_LOOKUP_TAG_KEY=$1
SNAPSHOT_LOOKUP_TAG_VALUE=$2
MOUNT_PATH=$3

DEVICE=$(lsblk | egrep " $MOUNT_PATH\$" | awk '{ print "/dev/"$1 }')
INSTANCE_ID=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/instance-id)
VOLUME_ID=$(aws ec2 describe-volumes --output json --query "Volumes[*].Attachments[*]" | jq -r ".[]|.[]|select(.Device==\"$DEVICE\" and .InstanceId==\"$INSTANCE_ID\").VolumeId")

if ! SNAPSHOT_ID=$(create_snapshot $VOLUME_ID $SNAPSHOT_LOOKUP_TAG_KEY $SNAPSHOT_LOOKUP_TAG_VALUE); then
  fail $ERROR
fi
if [ "$WAIT" ]; then
  COUNTER=0
  while [  $COUNTER -lt $WAIT_TIME ] && [ "$SNAPSHOT_STATUS" != "completed" ]; do
    sleep 1
    SNAPSHOT_STATUS=$(aws ec2 describe-snapshots --snapshot-ids $SNAPSHOT_ID | jq -r ".Snapshots[0].State")
    COUNTER=$(($COUNTER+1))
  done
  if [ "$SNAPSHOT_STATUS" != "completed" ]; then
    fail "Failed to complete snapshot"
  fi
fi
echo $SNAPSHOT_ID
