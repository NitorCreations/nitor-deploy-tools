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

from setuptools import setup

setup(name='nitor_deploy_tools',
      version='0.50',
      description='Utilities for deploying with Nitor aws-utils',
      url='http://github.com/NitorCreations/nitor-deploy-tools',
      download_url = 'https://github.com/NitorCreations/nitor-deploy-tools/tarball/0.50',
      author='Pasi Niemi',
      author_email='pasi@nitor.com',
      license='Apache 2.0',
      packages=['vault', 'n_utils'],
      include_package_data=True,
      scripts=[
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
      ],
      entry_points = {
        'console_scripts': [
            'vault=vault.cli:main',
            'assume-role=n_utils.cli:assume_role',
            'list-file-to-json=n_utils.cli:list_file_to_json',
            'create-userid-list=n_utils.cli:create_userid_list',
            'add-deployer-server=n_utils.cli:add_deployer_server',
            'yaml-to-json=n_utils.cli:yaml_to_json',
            'json-to-yaml=n_utils.cli:json_to_yaml',
            'pytail=n_utils.cli:read_and_follow',
            'n-utils-init=n_utils.cf_utils:init',
            'n-utils-resolve-include=n_utils.cli:resolve_include',
            'n-include=n_utils.cli:resolve_include',
            'cf-delete-stack=n_utils.cli:delete_stack',
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
            'cf-update-stack=n_utils.cli:update_stack',
            'associate-eip=n_utils.cli:associate_eip',
            'ec2-associate-eip=n_utils.cli:associate_eip',
            'ec2-instance-id=n_utils.cli:instance_id',
            'ec2-region=n_utils.cli:region',
            'ec2-get-userdata=n_utils.cli:get_userdata',
        ],
      },
      install_requires=[
          'pyaml',
          'boto3',
          'pycrypto',
          'requests',
          'termcolor'
      ],
      zip_safe=False)
