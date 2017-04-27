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

fail() {
  echo $1
  exit 1
}

set -x

source $(n-include ebs-functions.sh)
SNAPSHOT_LOOKUP_TAG_KEY=$1
SNAPSHOT_LOOKUP_TAG_VALUE=$2
MOUNT_PATH=$3
SIZE_GB=$4

if [ $# -lt 3 ]; then
  fail "Usage: $0 <tag key> <tag value> <mount path> [<empty volume size in gb>]"
fi

if ! SNAPSHOT_ID=$(find_latest_snapshot $SNAPSHOT_LOOKUP_TAG_KEY $SNAPSHOT_LOOKUP_TAG_VALUE); then
  if ! VOLUME_ID=$(create_empty_volume $SIZE_GB); then
    fail $ERROR
  fi
  EMPTY_VOLUME=1
elif ! VOLUME_ID=$(create_volume $SNAPSHOT_ID $SIZE_GB); then
  fail $ERROR
fi

aws ec2 create-tags --resources $VOLUME_ID --tags Key=$SNAPSHOT_LOOKUP_TAG_KEY,Value=$SNAPSHOT_LOOKUP_TAG_VALUE

for LETTER in c d e f g h i; do
  if [ ! -e /dev/xvd$LETTER ]; then
    DEVICE=/dev/xvd$LETTER
    break
  fi
done

if [ -z "$DEVICE" ]; then
  fail "Free device not found."
fi

if ! attach_volume $VOLUME_ID $DEVICE; then
  fail $ERROR
fi

if [ -n "$EMPTY_VOLUME" ]; then
  mkfs.ext4 $DEVICE
else
  SNAPSHOT_SIZE=$(aws ec2 describe-snapshots --snapshot-ids $SNAPSHOT_ID | jq -r ".Snapshots[0]|.VolumeSize")
  if [ "$SNAPSHOT_SIZE" != "$SIZE_GB" ]; then
    e2fsck -f -p $DEVICE
    if [ $? -gt 2 ]; then
      fail "e2fsck failed"
    fi
    resize2fs $DEVICE
  fi
fi

delete_on_termination $DEVICE
# set up cron snapshots

# mount volume
mkdir -p $MOUNT_PATH
mount $DEVICE $MOUNT_PATH
