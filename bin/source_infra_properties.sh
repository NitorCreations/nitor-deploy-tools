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

# This script sources the infra*.properties files in the standard fashion. The image and stack name must be provided as arguments if applicable, otherwise an empty argument should be given instead e.g. ""
# example: source source_infra_properties.sh "jenkins" "bob-jenkins"
if [ "$_ARGCOMPLETE" ]; then
  # Handle command completion executions
  unset _ARGCOMPLETE
  source $(n-include autocomplete-helpers.sh)
  case $COMP_CWORD in
    2)
      compgen -W "$(get_stack_dirs)" -- $COMP_CUR
      ;;
    3)
      compgen -W "$(get_dockers $COMP_PREV) $(get_stacks $COMP_PREV)" -- $COMP_CUR
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi
[ "$GIT_BRANCH" ] || GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

source_first_existing() {
  for PROPFILE in "$@"; do
    if [ -e "$PROPFILE" ]; then
      source "$PROPFILE"
      return
    fi
  done
}

image="$1" ; shift
ORIG_STACK_NAME="$1"
ORIG_DOCKER_NAME="$1"
shift

# by default, prefix stack name with branch name, to avoid accidentally using same names in different branches - override in infra-<branch>.properties to your liking. STACK_NAME and ORIG_STACK_NAME can be assumed to exist.
STACK_NAME="${GIT_BRANCH##*/}-${ORIG_STACK_NAME}"
DOCKER_NAME="$image/${GIT_BRANCH##*/}-${ORIG_STACK_NAME}"

sharedpropfile="infra.properties"
imagesharedpropfile="${image}/${sharedpropfile}"
stacksharedpropfile="${image}/stack-${ORIG_STACK_NAME}/${sharedpropfile}"
dockersharedpropfile="${image}/docker-${ORIG_STACK_NAME}/${sharedpropfile}"

infrapropfile="infra-${GIT_BRANCH##*/}.properties"
imagepropfile="${image}/${infrapropfile}"
stackpropfile="${image}/stack-${ORIG_STACK_NAME}/${infrapropfile}"
dockerpropfile="${image}/docker-${ORIG_STACK_NAME}/${infrapropfile}"

source_first_existing "$sharedpropfile"
source_first_existing "$infrapropfile"
source_first_existing "$imagesharedpropfile"
source_first_existing "$imagepropfile"
source_first_existing "$stacksharedpropfile" "$dockersharedpropfile"
source_first_existing "$stackpropfile" "$dockerpropfile"

#If region not set in infra files, get the region of the instance or from env
[ "$REGION" ] || REGION=$(ec2-region)

# Same logic as above for account id
[ "$ACCOUNT_ID" ] || ACCOUNT_ID=$(account-id)
unset source_first_existing
