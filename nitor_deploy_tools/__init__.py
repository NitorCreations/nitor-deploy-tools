#!/usr/bin/env python

# Copyright 2016 Nitor Creations Oy
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
import boto3
import json
from Crypto.Cipher import AES
from Crypto.Util import Counter

cf = boto3.client('cloudformation')
kms = boto3.client('kms')
prefix = "default"

def get_cipher(key):
  ctr = Counter.new(128, initial_value=1337)
  return AES.new(key, AES.MODE_CTR, counter=ctr)

def get_cf_params(stackName):
  stack = cf.describe_stacks(StackName=stackName)
  ret = {}
  for output in  stack['Stacks'][0]['Outputs']:
      if output['OutputKey'] == 'vaultBucketName':
          ret['bucketName'] = output['OutputValue']
      if output['OutputKey'] == 'kmsKeyArn':
          ret['keyArn'] = output['OutputValue']
  return ret

def encrypt(keyArn, data):
  ret = {}
  keyDict = kms.generate_data_key(KeyId=keyArn, KeySpec="AES_256")
  datakey = keyDict['Plaintext']
  ret['dataKey'] = keyDict['CiphertextBlob']
  cipher = get_cipher(datakey)
  ret['cipherText'] = cipher.encrypt(data)
  return ret

def decrypt(key, encrypted):
  decrypted_key = kms.decrypt(CiphertextBlob=key)['Plaintext']
  cipher = get_cipher(decrypted_key)
  return cipher.decrypt(encrypted)
