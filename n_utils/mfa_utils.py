#!/usr/bin/env python

# Copyright 2017 Nitor Creations Oy
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
# limitations under the License
import os
import yaml
import pyotp
import sys

from .enc_utils import _encrypt, _decrypt

def mfa_add_token(args):
    """ Adds or overwrites an MFA token to be used with role assumption.
        Tokens will be saved in a .ndt subdirectory in the user's home directory. """
    ndt_dir = get_ndt_dir()
    if not os.path.exists(ndt_dir):
        os.makedirs(ndt_dir)
    data = {
        'token_name': args.token_name,
        'token_arn': args.token_arn,
        'token_secret': "enc--" + _encrypt(args.token_secret)
    }
    token_file = ndt_dir + '/mfa_' + args.token_name
    if os.path.isfile(token_file) and not args.force:
        raise ValueError('A token with the name ' + args.token_name + ' already exists!')
    with open(token_file, 'w') as outfile:
        os.chmod(token_file, 0600)
        yaml.dump(data, outfile, default_flow_style=False)

def mfa_read_token(token_name):
    """ Reads a previously added MFA token file and returns its data. """
    data = None
    with open(get_ndt_dir() + '/mfa_' + token_name, 'r') as infile:
        try:
            data = yaml.load(infile)
        except yaml.YAMLError as exc:
            print exc
    if data:
        if not data['token_secret'].startswith("enc--"):
            data['force'] = True
            mfa_add_token(Struct(**data))
            return mfa_read_token(token_name)
    return data

def get_ndt_dir():
    """ Gets cross platform ndt directory path. Makes sure it exists. """
    ndt_dir = os.path.expanduser("~/.ndt")
    if not os.path.exists(ndt_dir):
        os.makedirs(ndt_dir)
    return ndt_dir

def mfa_generate_code(token_name):
    """ Generates an MFA code with the specified token. """
    token = mfa_read_token(token_name)
    if token['token_secret'].startswith("enc--"):
        secret = _decrypt(token['token_secret'][5:])
    else:
        secret = token['token_secret']
    totp = pyotp.TOTP(secret)
    return totp.now()

def mfa_generate_code_with_secret(secret):
    """ Generates an MFA code using the secret passed in. """
    if secret.startswith("enc--"):
        secret = _decrypt(secret[5:])
    totp = pyotp.TOTP(secret)
    return totp.now()

def mfa_delete_token(token_name):
    """ Deletes an MFA token file from the .ndt subdirectory in the user's
        home directory """
    os.remove(get_ndt_dir() + '/mfa_' + token_name)
class Struct ( object ) :
    def __init__ ( self , ** entries ) :
        self . __dict__ . update ( entries )
