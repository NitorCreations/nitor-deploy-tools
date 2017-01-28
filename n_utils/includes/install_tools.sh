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

set -xe

if [ -z "$1" ]; then
  AWSUTILS_VERSION=0.73
else
  AWSUTILS_VERSION="$1"
fi

UTILS_VERSION=$AWSUTILS_VERSION
curl -Ls https://github.com/NitorCreations/aws-utils/archive/$UTILS_VERSION.tar.gz | tar -xzf - --strip 1 -C /
echo $AWSUTILS_VERSION > /opt/nitor/aws-utils.version

source /opt/nitor/common_tools.sh
ln -snf /usr/bin/lpass_$(system_type_and_version) /usr/bin/lpass
pip install -U pip setuptools nitor-deploy-tools awscli boto3
