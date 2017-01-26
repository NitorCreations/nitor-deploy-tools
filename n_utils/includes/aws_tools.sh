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

source "$(dirname "${BASH_SOURCE[0]}")/common_tools.sh"

# Optional parameters in CloudFormation stack: paramEipAllocationId OR paramEip
# Required template policies when CF_paramEipAllocationId is used: ec2:AssociateAddress
# Required template policies when CF_paramEip is used: ec2:AssociateAddress, ec2:DescribeAddresses
aws_ec2_associate_address () {
  associate-eip
}

# Required parameters in CloudFormation: CF_AWS__Region, CF_AWS__StackName
aws_install_metadata_files () {
  [ "$CF_AWS__StackName" ] || CF_AWS__StackName = "$(jq -r .FullStackData.StackName < /opt/nitor/instance-data.json)"
  [ "$CF_AWS__Region" ] || CF_AWS__Region = "$(jq -r .FullStackData.StackId < /opt/nitor/instance-data.json | cut -d: -f 4)"
  check_parameters CF_AWS__StackName CF_AWS__Region
  cfn-init -v --stack "${CF_AWS__StackName}" --resource resourceLc --region "${CF_AWS__Region}"
}
