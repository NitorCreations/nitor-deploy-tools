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

if [ -z "$1" -o "$1" = "latest" ]; then
  DEPLOYTOOLS_VERSION=""
else
  DEPLOYTOOLS_VERSION="==$1"
fi

pip install -U pip setuptools awscli boto3 "nitor-deploy-tools$DEPLOYTOOLS_VERSION"
source $(n-include common_tools.sh)
