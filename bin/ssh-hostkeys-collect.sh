#!/bin/bash -e

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

host="$1"
if [ ! "$host" -o "$host" = "--help" ]; then
   echo "usage: $0 <hostname>" >&2
   echo "Creates a <hostname>-ssh-hostkeys.sh archive in the current directory" >&2
   exit 10
fi
create-shell-archive.sh /etc/ssh/ssh_host_* > ${host}-ssh-hostkeys.sh 
chmod og= ${host}-ssh-hostkeys.sh
