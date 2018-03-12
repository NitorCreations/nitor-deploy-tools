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
  echo '-h'
  compgen -f -- $COMP_CUR
  exit 0
fi

usage() {
  echo "usage: $0 [<file> ...]" >&2
  echo "" >&2
  echo "Creates a self-extracting bash archive, suitable for storing in e.g. Lastpass SecureNotes" >&2
  exit 1
}

if [ "$1" = "--help" -o "$1" = "-h" ]; then
  usage
fi

eof_marker="AR_EOF_MARKER_$(basename $(mktemp --dry-run | tr . _))"
echo '#!/bin/bash -e'
echo 'umask 077'
for file ; do
    echo 'echo "Extracting '"$file"'"'
    [ -e "$file" ]
    echo 'cat > "'"$file"'" << '\'$eof_marker\'' || { echo "ERROR extracting file" ; exit 1 ; }'
    cat "$file"
    echo $eof_marker
    mode=$(stat -c '%a' "$file")
    echo 'chmod '"$mode"' "'"$file"'"'
done
