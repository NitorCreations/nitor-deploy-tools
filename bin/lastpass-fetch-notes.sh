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

mode="$1"
shift

if [ ! "$mode" ]; then
  echo "usage: $0 <mode> [<file> ...] [--optional <file> ...]" >&2
  echo "Files specified after --optional won't fail if the file does not exist."
  exit 1
fi

for path ; do
  if [ "$path" = "--optional" ]; then
    optional=1
    continue
  fi
  FNAME="$(basename "$path")"
  DNAME="$(dirname "$path")"
  if ! mkdir -p "$DNAME" || ! lpass show --notes "$FNAME" > "$path"; then
    if [ ! "$optional" ]; then
      echo "ERROR: Failed to get file $path"
      exit 1
    else
      echo "Optional file $path not found"
      rm -f $path
    fi
  else
    chmod $mode $path
    echo "Fetched $path"
  fi
done
