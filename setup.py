from setuptools import setup

setup(name='nitor_deploy_tools',
      version='0.1',
      description='Utilities for deploying with Nitor aws-utils',
      url='http://github.com/NitorCreations/nitor-deploy-tools',
      author='Pasi Niemi',
      author_email='pasi@nitor.com',
      license='Apache 2.0',
      packages=['vault'],
      entry_points = {
        'console_scripts': ['vault=vault.cli:main'],
      },
      install_requires=[
          'boto3',
          'pycrypto'
      ],
      zip_safe=False)
