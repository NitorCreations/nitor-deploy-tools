#!/usr/bin/env python
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
