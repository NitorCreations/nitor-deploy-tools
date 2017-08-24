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
      compgen -W "$(get_dockers $COMP_PREV)" -- $COMP_CUR
      ;;
    *)
      exit 1
      ;;
  esac
  exit 0
fi

set -xe

die () {
  echo "$@" >&2
  exit 1
}

image="$1" ; shift
[ "${image}" ] || die "You must give the image name as argument"
docker="$1"; shift
[ "${docker}" ] || die "You must give the docker name as argument"

TSTAMP=$(date +%Y%m%d%H%M%S)
if [ -z "$BUILD_NUMBER" ]; then
  BUILD_NUMBER=$TSTAMP
else
  BUILD_NUMBER=$(printf "%04d\n" $BUILD_NUMBER)
fi

source source_infra_properties.sh "$image" "$docker"

if [ -x "$image/docker-$ORIG_DOCKER_NAME/pre_build.sh" ]; then
  cd "$image/docker-$ORIG_DOCKER_NAME"
  "./pre_build.sh"
  cd ../..
fi
sudo docker build -t "$DOCKER_NAME" "$image/docker-$ORIG_DOCKER_NAME"

#If assume-deploy-role.sh is on the path, run it to assume the appropriate role for deployment
if [ -n "$DEPLOY_ROLE_ARN" ] && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(ndt assume-role $DEPLOY_ROLE_ARN)
elif which assume-deploy-role.sh > /dev/null && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(assume-deploy-role.sh)
fi

eval "$(ndt ecr-ensure-repo $DOCKER_NAME)"
sudo docker tag $DOCKER_NAME:latest $DOCKER_NAME:$BUILD_NUMBER
sudo docker tag $DOCKER_NAME:latest $REPO:latest
sudo docker tag $DOCKER_NAME:$BUILD_NUMBER $REPO:$BUILD_NUMBER
sudo docker push $REPO:latest
sudo docker push $REPO:$BUILD_NUMBER
