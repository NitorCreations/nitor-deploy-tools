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

#If region not set in infra files, get the region of the instance
[ "$REGION" ] || REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')
#If not running on an AWS instance, get the region configured for aws tools
[ "$REGION" ] || REGION=$(aws configure list | grep region | awk '{ print $2 }')

# Same logic as above for account id
[ "$ACCOUNT_ID" ] || ACCOUNT_ID=$(curl -s  http://169.254.169.254/latest/dynamic/instance-identity/document | grep accountId | awk -F\" '{print $4}')
[ "$ACCOUNT_ID" ] || ACCOUNT_ID=$(aws iam get-user | grep Arn | awk -NF: '{ print $6 }')
