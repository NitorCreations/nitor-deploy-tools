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

if [ "$_ARGCOMPLETE" ]; then
  unset _ARGCOMPLETE
  source $(n-include autocomplete-helpers.sh)
  # Handle command completion executions
  COMP_WORDS=( $COMP_LINE )
  if [ "${COMP_WORDS[2]}" = "-d" ]; then 
    COMP_INDEX=$(($COMP_CWORD - 1))
    IMAGE_DIR=${COMP_WORDS[3]}
    STACK=${COMP_WORDS[4]}
  else
    COMP_INDEX=$COMP_CWORD
    IMAGE_DIR=${COMP_WORDS[2]}
    STACK=${COMP_WORDS[3]}
  fi
  IMAGE=$(echo $IMAGE_DIR| tr "-" "_")
  case $COMP_INDEX in
    2)
      if [ "$COMP_INDEX" = "$COMP_CWORD" ]; then
        DRY="-d "
      fi
      compgen -W "$DRY$(get_stack_dirs)" -- $COMP_CUR
      ;;
    3)
      compgen -W "$(get_stacks $IMAGE_DIR)" -- $COMP_CUR
      ;;
    4)
      source source_infra_properties.sh $IMAGE $STACK
      JOB_NAME="${JENKINS_JOB_PREFIX}_${IMAGE}_bake"
      IMAGE_IDS="$(get_imageids $IMAGE_DIR $JOB_NAME)"
      compgen -W "$IMAGE_IDS" -- $COMP_CUR
      ;;
    5)
      source source_infra_properties.sh $IMAGE $STACK
      echo "${JENKINS_JOB_PREFIX}_${IMAGE}_bake"
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi
source $(n-include autocomplete-helpers.sh)

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

if [ -z "$AMI_ID" ]; then
  AMI_ID="$(ndt get-images $IMAGE_JOB | head -1 | cut -d: -f1)"
fi

#If assume-deploy-role.sh is on the path, run it to assume the appropriate role for deployment
if [ -n "$DEPLOY_ROLE_ARN" ] && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(ndt assume-role $DEPLOY_ROLE_ARN)
elif which assume-deploy-role.sh > /dev/null && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(assume-deploy-role.sh)
fi

for DOCKER in $(get_dockers $image); do
  unset BAKE_IMAGE_BRANCH DOCKER_NAME
  eval "$(job_properties ${GIT_BRANCH##*/} $image $DOCKER | egrep '^DOCKER_NAME=|^BAKE_IMAGE_BRANCH=')"
  if [ -n "$BAKE_IMAGE_BRANCH" ] && [ "${GIT_BRANCH##*/}" != "$BAKE_IMAGE_BRANCH" ]; then
    checkout_branch $BAKE_IMAGE_BRANCH
    cd $BAKE_IMAGE_BRANCH-checkout
    eval "$(job_properties $BAKE_IMAGE_BRANCH $image $DOCKER | egrep '^DOCKER_NAME=')"
    cd ..
    rm -rf $BAKE_IMAGE_BRANCH-checkout
  fi
  DOCKER_PARAM_NAME="paramDockerUri$DOCKER"
  URI="$(ndt ecr-repo-uri $DOCKER_NAME)"
  [ "$URI" ] && eval "$DOCKER_PARAM_NAME=$URI"
done
export $(set | egrep -o '^param[a-zA-Z0-9_]+=' | tr -d '=') # export any param* variable defined in the infra-<branch>.properties files

export AMI_ID IMAGE_JOB CF_BUCKET DEPLOY_ROLE_ARN

cf-update-stack "${STACK_NAME}" "${image}/stack-${ORIG_STACK_NAME}/template.yaml" "$REGION" $DRY_RUN
