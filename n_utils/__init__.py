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

""" Main module for nitor-deploy-tools
"""

SCRIPTS = [
    'bin/bake-image.sh',
    'bin/create-shell-archive.sh',
    'bin/deploy-stack.sh',
    'bin/encrypt-and-mount.sh',
    'bin/ensure-letsencrypt-certs.sh',
    'bin/hook.sh',
    'bin/lastpass-fetch-notes.sh',
    'bin/lastpass-login.sh',
    'bin/lastpass-logout.sh',
    'bin/letsencrypt.sh',
    'bin/lpssh',
    'bin/s3-role-download.sh',
    'bin/setup-fetch-secrets.sh',
    'bin/show-stack-params-and-outputs.sh',
    'bin/snapshot-from-volume.sh',
    'bin/source_infra_properties.sh',
    'bin/ssh-hostkeys-collect.sh',
    'bin/undeploy-stack.sh',
    'bin/volume-from-snapshot.sh'
]
NDT_AND_CONSOLE = [
    'assume-role=n_utils.cli:assume_role',
    'list-file-to-json=n_utils.cli:list_file_to_json',
    'add-deployer-server=n_utils.cli:add_deployer_server',
    'yaml-to-json=n_utils.cli:yaml_to_json',
    'json-to-yaml=n_utils.cli:json_to_yaml',
    'pytail=n_utils.cli:read_and_follow',
    'n-utils-init=n_utils.cf_utils:init',
    'n-include=n_utils.cli:resolve_include',
    'account-id=n_utils.cli:get_account_id',
    'cf-follow-logs=n_utils.cli:tail_stack_logs',
    'cf-logical-id=n_utils.cli:logical_id',
    'logs-to-cloudwatch=n_utils.cli:logs_to_cloudwatch',
    'cf-logs-to-cloudwatch=n_utils.cli:logs_to_cloudwatch',
    'cf-region=n_utils.cli:cf_region',
    'signal-cf-status=n_utils.cli:signal_cf_status',
    'cf-get-parameter=n_utils.cli:get_parameter',
    'cf-signal-status=n_utils.cli:signal_cf_status',
    'cf-stack-name=n_utils.cli:stack_name',
    'cf-stack-id=n_utils.cli:stack_id',
    'associate-eip=n_utils.cli:associate_eip',
    'ec2-associate-eip=n_utils.cli:associate_eip',
    'ec2-clean-snapshots=n_utils.cli:clean_snapshots',
    'ec2-instance-id=n_utils.cli:instance_id',
    'ec2-region=n_utils.cli:ec2_region',
    'ec2-get-userdata=n_utils.cli:get_userdata',
    'detach-volume=n_utils.cli:detach_volume',
]
NDT_ONLY = [
    'setup-cli=n_utils.cli:setup_cli',
    'setup-networks=n_utils.cli:setup_networks',
    'volume-from-snapshot=n_utils.cli:volume_from_snapshot',
    'snapshot-from-volume=n_utils.cli:snapshot_from_volume',
    'show-stack-params-and-outputs=n_utils.cli:show_stack_params_and_outputs',
    'get-images=n_utils.cli:cli_get_images',
    'promote-image=n_utils.cli:cli_promote_image',
    'share-to-another-region=n_utils.cli:cli_share_to_another_region',
    'register-private-dns=n_utils.cli:cli_register_private_dns'
]
NDT_ONLY_SCRIPT = [
    'list-jobs.sh'
]
CONSOLE_ONLY = [
    'cf-delete-stack=n_utils.cli:delete_stack',
    'cf-update-stack=n_utils.cli:update_stack',
    'ndt=n_utils.cli:ndt',
    'nitor-dt-register-complete=n_utils.cli:ndt_register_complete',
    'latest-snapshot=n_utils.volumes:latest_snapshot'
]
CONSOLESCRIPTS = CONSOLE_ONLY + NDT_AND_CONSOLE
COMMAND_MAPPINGS = {}
for script in SCRIPTS:
    name = script.split("/")[-1]
    value = "script"
    if name.endswith(".sh"):
        name = name[:-3]
        value = "shell"
    COMMAND_MAPPINGS[name] = value
for script in NDT_ONLY_SCRIPT:
    name = script
    value = "ndtscript"
    if name.endswith(".sh"):
        name = name[:-3]
        value = "ndtshell"
    COMMAND_MAPPINGS[name] = value
for script in NDT_AND_CONSOLE + NDT_ONLY:
    name = script.split("=")[0]
    value = script.split("=")[1]
    COMMAND_MAPPINGS[name] = value
