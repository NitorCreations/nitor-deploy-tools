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

# Find the latest snapshot with a tag key and value
# Usage: find_latest_snapshot tag_key tag_value
find_latest_snapshot() {
  set_region
  local SNAPSHOT_LOOKUP_TAG_KEY=$1
  local SNAPSHOT_LOOKUP_TAG_VALUE=$2
  local SNAPSHOT_ID=$(aws ec2 describe-snapshots --filter 'Name=tag:'$SNAPSHOT_LOOKUP_TAG_KEY',Values='$SNAPSHOT_LOOKUP_TAG_VALUE | jq -r '.[]|max_by(.StartTime)|.SnapshotId')
  if [ -z "$SNAPSHOT_ID" -o "$SNAPSHOT_ID" = "null" ]; then
    ERROR="No snapshots found"
    return 1
  fi
  local SNAPSHOT_STATUS=$(aws ec2 describe-snapshots --snapshot-ids $SNAPSHOT_ID | jq -r '.[]|.[]|.State')
  local COUNTER=0
  while [  $COUNTER -lt 180 ] && [ "$SNAPSHOT_STATUS" != "completed" ]; do
   sleep 1
   SNAPSHOT_STATUS=$(aws ec2 describe-snapshots --snapshot-ids $SNAPSHOT_ID | jq -r '.[]|.[]|.State')
   COUNTER=$(($COUNTER+1))
  done
  if [ $COUNTER -eq 180 ]; then
    ERROR="Latest data volume snapshot not in completed state!"
    return 1
  else
    echo "$SNAPSHOT_ID"
    return 0
  fi
}

# Create new volume from snapshot
# Usage: create_volume snapshot-id [size_gb]
create_volume() {
  local SNAPSHOT_ID=$1
  local SIZE_GB=$2
  if [ -n "$SIZE_GB" ]; then
    local SIZE="--size $SIZE_GB"
  fi
  local AVAILABILITY_ZONE=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/placement/availability-zone)
  local VOLUME_ID=$(aws ec2 create-volume $SIZE --snapshot-id $SNAPSHOT_ID --availability-zone $AVAILABILITY_ZONE --volume-type gp2 | jq -r '.VolumeId')
  local VOLUME_STATUS=$(aws ec2 describe-volumes --volume-ids $VOLUME_ID | jq -r '.Volumes[].State')
  local COUNTER=0
  while [  $COUNTER -lt 180 ] && [ "$VOLUME_STATUS" != "available" ]; do
    sleep 1
    VOLUME_STATUS=$(aws ec2 describe-volumes --volume-ids $VOLUME_ID | jq -r '.Volumes[].State')
    COUNTER=$(($COUNTER+1))
  done
  if [ $COUNTER -eq 180 ]; then
    ERROR="Volume creation failed!"
    return 1
  else
    echo "$VOLUME_ID"
    return 0
  fi
}

# Create new empty volume
# Usage: create_empty_volume size_gb
create_empty_volume() {
  local SIZE_GB=$1
  local AVAILABILITY_ZONE=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/placement/availability-zone)
  local VOLUME_ID=$(aws ec2 create-volume --size $SIZE_GB --availability-zone $AVAILABILITY_ZONE --volume-type gp2 | jq -r '.VolumeId')
  local VOLUME_STATUS=$(aws ec2 describe-volumes --volume-ids $VOLUME_ID | jq -r '.Volumes[].State')
  local COUNTER=0
  while [  $COUNTER -lt 180 ] && [ "$VOLUME_STATUS" != "available" ]; do
    sleep 1
    VOLUME_STATUS=$(aws ec2 describe-volumes --volume-ids $VOLUME_ID | jq -r '.Volumes[].State')
    COUNTER=$(($COUNTER+1))
  done
  if [ $COUNTER -eq 180 ]; then
    ERROR="Volume creation failed!"
    return 1
  else
    echo "$VOLUME_ID"
    return 0
  fi
}

# Attach volume
# Usage: attach_volume volume-id device-path
attach_volume() {
  local VOLUME_ID=$1
  local DEVICE_PATH=$2
  local INSTANCE_ID=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/instance-id)
  local VOLUME_ATTACHMENT_STATUS=$(aws ec2 attach-volume --volume-id $VOLUME_ID --instance-id $INSTANCE_ID --device $DEVICE_PATH | jq -r '.State')
  local COUNTER=0
  while [  $COUNTER -lt 180 ] && [ "$VOLUME_ATTACHMENT_STATUS" != "attached" ]; do
    sleep 1
    VOLUME_ATTACHMENT_STATUS=$(aws ec2 describe-volumes --volume-ids $VOLUME_ID | jq -r '.Volumes[].Attachments[].State')
    COUNTER=$(($COUNTER+1))
  done
  if [ $COUNTER -eq 180 ]; then
    ERROR="Volume attachment failed!"
    return 1
  else
    return 0
  fi
}

# Set volume to be deleted on instance termination. Snapshots will remain.
# Usage: delete_on_termination device-path
delete_on_termination() {
  local INSTANCE_ID=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/instance-id)
  local DEVICE_PATH=$1
  aws ec2 modify-instance-attribute --instance-id $INSTANCE_ID --block-device-mappings "[{\"DeviceName\": \"$DEVICE_PATH\",\"Ebs\":{\"DeleteOnTermination\":true}}]"
}

# Create snapshot from volume and tag it so it can be found by e.g. find_latest_snapshot
# For data consistency, it may be a good idea to unmount the volume first.
# Usage: create_snapshot volume_id tag_key tag_value
create_snapshot() {
  local VOLUME_ID=$1
  local TAG_KEY=$2
  local TAG_VALUE=$3
  local SNAPSHOT_ID=$(aws ec2 create-snapshot --volume-id $VOLUME_ID | jq -r '.SnapshotId')
  if [ "$SNAPSHOT_ID" != "" ]; then
    echo $SNAPSHOT_ID
  else
    ERROR="Snapshot creation failed!"
    return 1
  fi

  if ! $(aws ec2 create-tags --resources $SNAPSHOT_ID --tags Key=$TAG_KEY,Value=$TAG_VALUE Key=Name,Value=$TAG_VALUE); then
    ERROR="Tagging snapshot failed!"
    return 1
  fi
}

# Delete old snapshots tagged with a specific key/value. Keep a number of latest snapshots.
# Usage: delete_old_snapshots tag_key tag_value number_to_keep
delete_old_snapshots() {
  local SNAPSHOT_LOOKUP_TAG_KEY=$1
  local SNAPSHOT_LOOKUP_TAG_VALUE=$2
  local KEEP=$3
  local TO_DELETE
  if ! TO_DELETE=$(aws ec2 describe-snapshots --filter 'Name=tag:'$SNAPSHOT_LOOKUP_TAG_KEY',Values='$SNAPSHOT_LOOKUP_TAG_VALUE | jq -r '.[]|sort_by(.StartTime)|reverse|.['$KEEP':]|.[]|.SnapshotId'); then
    ERROR="Lookup for snapshots failed!"
    return 1
  fi
  local ERRORS=0
  for i in $TO_DELETE;
  do
    aws ec2 delete-snapshot --snapshot-id $i
    ERRORS=$(($ERRORS+$?))
  done
  return $ERRORS
}
