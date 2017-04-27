#!/bin/bash

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
if [ "$_ARGCOMPLETE" ]; then
  # Handle command completion executions
  exit 0
fi

set -e

if [ $# != 2 ]; then
  echo usage: $0 region stack-name
  exit 1
fi

aws cloudformation describe-stacks --region "$1" --stack-name "$2" | \
  jq  '[ .Stacks[] |
           ( .Parameters[]? | { (.ParameterKey): .ParameterValue } )
           ,
           ( .Outputs[]?    | { (.OutputKey):    .OutputValue } )
       | to_entries ] | add | from_entries'
