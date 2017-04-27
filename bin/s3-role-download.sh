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

if ! curl -sf --connect-timeout 3 http://169.254.169.254/latest/meta-data/iam/security-credentials/$1 > /dev/null; then
  ROLE=$(curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/iam/security-credentials/ | head -n 1)
  BUCKET=$1
  shift
  FILE=$1
  shift
else
  ROLE=$1
  shift
  BUCKET=$1
  shift
  FILE=$1
  shift
fi
if [ -z "$1" ]; then
  OUT=$(basename ${FILE})
  OUTARG=-o
elif [ "$1" = "-" ]; then
  OUT=
  OUTARG=
else
  OUT=$1
  OUTARG=-o
fi

CONTENT_TYPE="application/octet-stream"
DATE=$(date -R)
RESOURCE="/${BUCKET}/${FILE}"
TMP=$(mktemp)
if ! curl -sf --connect-timeout 3 http://169.254.169.254/latest/meta-data/iam/security-credentials/${ROLE} \
| egrep ^[[:space:]]*\" | sed 's/[^\"]*\"\([^\"]*\)\".:.\"\([^\"]*\).*/\1=\2/g' > $TMP; then
  echo "Failed to get credentials"
  exit 1
fi
source $TMP
rm -f $TMP
SIGNSTR="GET\n\n${CONTENT_TYPE}\n${DATE}\nx-amz-security-token:${Token}\n${RESOURCE}"
SIGNATURE=$(echo -en ${SIGNSTR} | openssl sha1 -hmac ${SecretAccessKey} -binary | base64)
exec curl -L -f -s $OUTARG $OUT  -X GET -H "Host: ${BUCKET}.s3.amazonaws.com" -H "Date: ${DATE}" -H "Content-Type: ${CONTENT_TYPE}" -H "Authorization: AWS ${AccessKeyId}:${SIGNATURE}" -H "x-amz-security-token: ${Token}" https://${BUCKET}.s3.amazonaws.com/${FILE}
