from setuptools import setup

setup(name='nitor_deploy_tools',
      version='0.10',
      description='Utilities for deploying with Nitor aws-utils',
      url='http://github.com/NitorCreations/nitor-deploy-tools',
      download_url = 'https://github.com/NitorCreations/nitor-deploy-tools/tarball/0.10',
      author='Pasi Niemi',
      author_email='pasi@nitor.com',
      license='Apache 2.0',
      packages=['vault'],
      scripts=['bin/source_infra_properties.sh', 'bin/show-stack-params-and-outputs.sh'],
      entry_points = {
        'console_scripts': [
            'vault=vault.cli:main',
            'yaml-to-json=n_utils.cli:yaml_to_json',
            'json-to-yaml=n_utils.cli:json_to_yaml',
            'pytail=n_utils.cli:read_and_follow',
            'logs-to-cloudwatch=n_utils.cli:logs_to_cloudwatch',
            'signal-cf-status=n_utils.cli:signal_cf_status',
            'associate-eip=n_utils.cli:associate_eip'
        ],
      },
      install_requires=[
          'boto3',
          'pycrypto',
          'requests'
      ],
      zip_safe=False)
