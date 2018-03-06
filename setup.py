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
import sys
from setuptools import setup
from n_utils import SCRIPTS, CONSOLESCRIPTS

setup(name='nitor_deploy_tools',
      version='0.223',
      description='Utilities for deploying with Nitor aws-utils',
      url='http://github.com/NitorCreations/nitor-deploy-tools',
      download_url='https://github.com/NitorCreations/nitor-deploy-tools/tarball/0.223',
      author='Pasi Niemi',
      author_email='pasi@nitor.com',
      license='Apache 2.0',
      packages=['n_utils'],
      include_package_data=True,
      scripts=SCRIPTS,
      entry_points={
          'console_scripts': CONSOLESCRIPTS,
      },
      install_requires=[
          'pyaml',
          'boto3',
          'awscli',
          'pycrypto',
          'requests',
          'termcolor',
          'ipaddr',
          'argcomplete',
          'nitor-vault',
          'psutil',
          'Pygments',
          'pyotp'
      ] + ([
          'win-unicode-console',
          'wmi',
          'pypiwin32'
          ] if sys.platform.startswith('win') else []),
      zip_safe=False)
