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
cache () {
  if ! [ -d .cache ]; then
      mkdir -p .cache
  fi
  args=${*}
  cachefile=.cache/"${args//[\"\'\ -\*]/_}"
  if [ -e "$cachefile" ]; then
    cat $cachefile
  else
    "$@" | tee $cachefile
  fi
}

if [ "$_ARGCOMPLETE" ]; then
  # Handle command completion executions
  case $COMP_CWORD in
    2)
      compgen -W "$(if [ -r infra.properties -o -r infra-master.properties ]; then find . -name 'infra-*.properties' | cut -d '/' -f 2 | grep -v 'infra.*.properties' | sort -u | tr "\n" " "; fi)" -- $COMP_CUR
      ;;
    3)
      compgen -W "$(if [ -r infra.properties -o -r infra-master.properties ]; then find $COMP_PREV -name 'stack-*' | sed 's/.*stack-\(.*\)/\1/g' | tr "\n" " "; fi)" -- $COMP_CUR
      ;;
    4)
      COMP_WORDS=( $COMP_LINE )
      IMAGE=$(echo ${COMP_WORDS[2]} | tr "-" "_")
      source source_infra_properties.sh ${COMP_WORDS[2]} ${COMP_WORDS[3]}
      JOB_NAME="${JENKINS_JOB_PREFIX}_${IMAGE}_bake"
      compgen -W "$(if [ -r infra.properties -o -r infra-master.properties ]; then cache aws ec2 describe-images --filters "Name=name,Values=[${JOB_NAME}*]" --query "Images[*].{ID:ImageId}" | jq -r .[].ID | tr "\n" " "; fi)" -- $COMP_CUR
      ;;
    5)
      COMP_WORDS=( $COMP_LINE )
      IMAGE=$(echo ${COMP_WORDS[2]} | tr "-" "_")
      source source_infra_properties.sh ${COMP_WORDS[2]} ${COMP_WORDS[3]}
      echo "${JENKINS_JOB_PREFIX}_${IMAGE}_bake"
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi

set -xe

if [ "$1" = "-d" ]; then
  DRY_RUN="--dry-run"
  shift
fi
image="$1" ; shift
stackName="$1" ; shift
AMI_ID="$1"
shift ||:
IMAGE_JOB="$1"
shift ||:

source source_infra_properties.sh "$image" "$stackName"
export $(set | egrep -o '^param[a-zA-Z0-9_]+=' | tr -d '=') # export any param* variable defined in the infra-<branch>.properties files
export AMI_ID IMAGE_JOB CF_BUCKET

#If assume-deploy-role.sh is on the path, run it to assume the appropriate role for deployment
if which assume-deploy-role.sh > /dev/null && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(assume-deploy-role.sh)
fi

cf-update-stack "${STACK_NAME}" "${image}/stack-${ORIG_STACK_NAME}/template.yaml" "$REGION" $DRY_RUN
