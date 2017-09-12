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

set -xe

if [ "$1" == "-f" ]; then
  FORCE="yes"; shift
fi

image="$1" ; shift
stackName="$1" ; shift

source source_infra_properties.sh "$image" "$stackName"
export AMI_ID IMAGE_JOB CF_BUCKET DEPLOY_ROLE_ARN

#If assume-deploy-role.sh is on the path, run it to assume the appropriate role for deployment
if [ -n "$DEPLOY_ROLE_ARN" ] && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(ndt assume-role $DEPLOY_ROLE_ARN)
elif which assume-deploy-role.sh > /dev/null && [ -z "$AWS_SESSION_TOKEN" ]; then
  eval $(assume-deploy-role.sh)
fi

# Delete will fail if S3 buckets have data - so delete those...
for BUCKET in $(aws --region $REGION cloudformation list-stack-resources --stack-name ${STACK_NAME} \
 | jq -r '.StackResourceSummaries[] | select(.ResourceType=="AWS::S3::Bucket")|.PhysicalResourceId'); do
   if [ -n "$FORCE" ]; then
     echo "force flag defined - deleting content of bucket $BUCKET"
     aws s3 rm s3://$BUCKET --recursive ||:
   else
     echo "force flag not defined - delete will fail if bucket $BUCKET is not empty"
   fi
done

ndt cf-delete-stack "${STACK_NAME}" "$REGION"
