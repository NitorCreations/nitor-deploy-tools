#!/bin/bash -ex

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

CF_AWS__StackName=""
CF_AWS__Region=""
CF_paramDnsName=""
CF_paramAwsUtilsVersion=""
CF_paramAmi=""
CF_paramAmiName=""
CF_paramEip=""
CF_paramSonatypeWorkSize="20"

export HOME=/root
cd $HOME

source /opt/nitor/cloud_init_functions.sh
source /opt/nitor/tool_installers.sh
AWSUTILS_VERSION="${CF_paramAwsUtilsVersion}" update_aws_utils
# reload scripts sourced above in case they changed:
source /opt/nitor/cloud_init_functions.sh
source /opt/nitor/tool_installers.sh

source /opt/nitor/apache_tools.sh
source /opt/nitor/ebs-functions.sh
source /opt/nitor/aws_tools.sh
source /opt/nitor/ssh_tools.sh
source /opt/nitor/nexus_tools.sh

set_region
aws_install_metadata_files
set_timezone
set_hostname

configure_and_start_nexus

apache_replace_domain_vars
apache_install_certs
apache_enable_and_start_service

nexus_wait_service_up
nexus_setup_snapshot_cron

ssh_install_hostkeys
ssh_restart_service

aws_ec2_associate_address

source /opt/nitor/cloud_init_footer.sh
