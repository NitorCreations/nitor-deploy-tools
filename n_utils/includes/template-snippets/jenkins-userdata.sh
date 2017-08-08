#!/bin/bash -x

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

CF_AWS__StackName=
CF_AWS__Region=
CF_paramAmiName=
CF_paramAdditionalFiles=
CF_paramAmi=
CF_paramDeployToolsVersion=
CF_paramJenkinsGit=
CF_paramDnsName=
CF_paramEip=
CF_paramEBSTag=
CF_paramEBSSize=32
CF_extraScanHosts=`#optional`
CF_paramMvnDeployId=`#optional`

export HOME=/root
cd $HOME

source $(n-include cloud_init_functions.sh)
source $(n-include tool_installers.sh)
update_aws_utils
# reload scripts sourced above in case they changed:
source $(n-include cloud_init_functions.sh)
source $(n-include tool_installers.sh)

source $(n-include aws_tools.sh)
source $(n-include ebs-functions.sh)
source $(n-include jenkins_tools.sh)
source $(n-include ssh_tools.sh)
source $(n-include apache_tools.sh)
source $(n-include ssh_tools.sh)

fail () {
    echo "FAIL: $@"
    exit 1
}
usermod -s /bin/bash jenkins
set_region
aws_install_metadata_files
set_timezone
set_hostname

apache_replace_domain_vars
apache_install_certs

jenkins_mount_ebs_home ${CF_paramEBSSize}
jenkins_discard_default_install
jenkins_setup_dotssh
jenkins_setup_snapshot_script
jenkins_setup_snapshot_on_shutdown
jenkins_setup_snapshot_job
jenkins_improve_config_security

jenkins_fetch_additional_files
jenkins_set_home
jenkins_enable_and_start_service

apache_enable_and_start_service

jenkins_wait_service_up

ssh_install_hostkeys
ssh_restart_service

aws_ec2_associate_address

source $(n-include cloud_init_footer.sh)
