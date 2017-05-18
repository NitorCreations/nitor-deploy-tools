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
      compgen -W "$(get_stacks $COMP_PREV)" -- $COMP_CUR
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi
[ "$GIT_BRANCH" ] || GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

image="$1" ; shift
ORIG_STACK_NAME="$1" ; shift

# by default, prefix stack name with branch name, to avoid accidentally using same names in different branches - override in infra-<branch>.properties to your liking. STACK_NAME and ORIG_STACK_NAME can be assumed to exist.
STACK_NAME="${GIT_BRANCH##*/}-${ORIG_STACK_NAME}"

sharedpropfile="infra.properties"
infrapropfile="infra-${GIT_BRANCH##*/}.properties"

[ -e "${sharedpropfile}" ] && source "${sharedpropfile}"
source "${infrapropfile}"
[ -e "${image}/${sharedpropfile}" ] && source "${image}/${sharedpropfile}"
[ -e "${image}/${infrapropfile}" ] && source "${image}/${infrapropfile}"
[ -e "${image}/stack-${ORIG_STACK_NAME}/${sharedpropfile}" ] && source "${image}/stack-${ORIG_STACK_NAME}/${sharedpropfile}"
[ -e "${image}/stack-${ORIG_STACK_NAME}/${infrapropfile}" ] && source "${image}/stack-${ORIG_STACK_NAME}/${infrapropfile}"

#If region not set in infra files, get the region of the instance or from env
[ "$REGION" ] || REGION=$(ec2-region)

# Same logic as above for account id
[ "$ACCOUNT_ID" ] || ACCOUNT_ID=$(account-id)
