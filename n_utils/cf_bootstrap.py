#!/usr/bin/env python

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

""" Utilities to bootsrap AWS accounts into use with nitor-deploy-tools
"""

import os
import stat

from awscli.customizations.configure.writer import ConfigFileWriter

def has_entry(prefix, name, file_name):
    if not os.path.isfile(file_name):
        return False
    with open(file_name, "r") as config:
        for line in config.readlines():
            if "[" + prefix + name + "]" == line.strip():
                return True
    return False

def setup_cli(name=None, key_id=None, secret=None, region=None):
    if name is None:
        name = raw_input("Profile name: ")
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, ".aws", "config")
    credentials_file = os.path.join(home_dir, ".aws", "credentials")
    if has_entry("profile ", name, config_file) or \
       has_entry("", name, credentials_file):
        print "Profile " + name + " already exists. Not overwriting."
        return
    if key_id is None:
        key_id = raw_input("Key ID: ")
    if secret is None:
        secret = raw_input("Key secret: ")
    if region is None:
        region = raw_input("Default region: ")
    writer = ConfigFileWriter()
    config_values = {
        "__section__": "profile " + name,
        "output": "json",
        "region": region
        }
    credentials_values = {
        "__section__": name,
        "aws_access_key_id": key_id,
        "aws_secret_access_key": secret
        }
    writer.update_config(config_values, config_file)
    writer.update_config(credentials_values, credentials_file)
    home_bin = credentials_file = os.path.join(home_dir, "bin")
    if not os.path.isdir(home_bin):
        os.makedirs(home_bin)
    source_file = os.path.join(home_bin, name)
    with open(source_file, "w") as source_script:
        source_script.write('#!/bin/bash\n\n')
        source_script.write('export AWS_DEFAULT_REGION=')
        source_script.write(region + ' AWS_PROFILE=' + name)
        source_script.write(' AWS_DEFAULT_PROFILE=' + name + "\n")
    os.chmod(source_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
