from setuptools import setup

setup(name='nitor_deploy_tools',
      version='0.30',
      description='Utilities for deploying with Nitor aws-utils',
      url='http://github.com/NitorCreations/nitor-deploy-tools',
      download_url = 'https://github.com/NitorCreations/nitor-deploy-tools/tarball/0.30',
      author='Pasi Niemi',
      author_email='pasi@nitor.com',
      license='Apache 2.0',
      packages=['vault', 'n_utils'],
      scripts=['bin/source_infra_properties.sh', 'bin/show-stack-params-and-outputs.sh'],
      entry_points = {
        'console_scripts': [
            'vault=vault.cli:main',
            'list-file-to-json=n_utils.cli:list_file_to_json',
            'create-userid-list=n_utils.cli:create_userid_list',
            'add-deployer-server=n_utils.cli:add_deployer_server',
            'yaml-to-json=n_utils.cli:yaml_to_json',
            'json-to-yaml=n_utils.cli:json_to_yaml',
            'pytail=n_utils.cli:read_and_follow',
            'logs-to-cloudwatch=n_utils.cli:logs_to_cloudwatch',
            'signal-cf-status=n_utils.cli:signal_cf_status',
            'associate-eip=n_utils.cli:associate_eip',
            'n-utils-init=n_utils.cf_utils:init',
            'ec2-instance-id=n_utils.cli:instance_id',
            'ec2-region=n_utils.cli:region',
            'cf-stack-name=n_utils.cli:stack_name',
            'cf-stack-id=n_utils.cli:stack_id',
            'cf-logical-id=n_utils.cli:logical_id',
            'cf-region=n_utils.cli:cf_region',
            'cf-update-stack=n_utils.cli:update_stack',
            'cf-delete-stack=n_utils.cli:delete_stack',
            'cf-follow-logs=n_utils.cli:tail_stack_logs'
        ],
      },
      install_requires=[
          'boto3',
          'pycrypto',
          'requests',
          'termcolor'
      ],
      zip_safe=False)
