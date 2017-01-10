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

import boto3
import os
from Crypto.Cipher import AES
from Crypto.Util import Counter
from botocore.exceptions import ClientError

class Vault(object):
    _session = boto3.Session()
    _kms = ""
    _prefix = ""
    _vault_key = ""
    _vault_bucket = ""
    def __init__(self, vault_stack="vault", vault_key="", vault_bucket="",
                 vault_iam_id="", vault_iam_secret="", vault_prefix=""):
        self._prefix = vault_prefix
        if self._prefix and not self._prefix.endswith("/"):
            self._prefix = self._prefix + "/"
        # Either use given vault iam credentials or assume that the environent has
        # some usable credentials (either through env vars or instance profile)
        if vault_iam_id and vault_iam_secret:
            self._session = boto3.Session(aws_access_key_id=vault_iam_id,
                                          aws_secret_access_key=vault_iam_secret)
        # And set up a kms client since all operations require that
        self._kms = self._session.client('kms')
        # Either use given vault kms key and/or vault bucket or look them up from a
        # cloudformation stack
        if vault_key:
            self._vault_key = vault_key
        elif "VAULT_KEY" in os.environ:
            self._vault_key = os.environ["VAULT_KEY"]
        if vault_bucket:
            self._vault_bucket = vault_bucket
        elif "VAULT_BUCKET" in os.environ:
            self._vault_key = os.environ["VAULT_BUCKET"]
        # If not given in constructor or environment, resolve from CloudFormation
        if not (self._vault_key and self._vault_bucket):
            stack_info = self._get_cf_params(vault_stack)
            if not self._vault_key:
                self._vault_key = stack_info['key_arn']
            if not self._vault_bucket:
                self._vault_bucket = stack_info['bucket_name']

    def _encrypt(self, data):
        ret = {}
        key_dict = self._kms.generate_data_key(KeyId=self._vault_key,
                                               KeySpec="AES_256")
        data_key = key_dict['Plaintext']
        ret['datakey'] = key_dict['CiphertextBlob']
        cipher = _get_cipher(data_key)
        ret['ciphertext'] = cipher.encrypt(data)
        return ret

    def _decrypt(self, data_key, encrypted):
        decrypted_key = self._kms.decrypt(CiphertextBlob=data_key)['Plaintext']
        cipher = _get_cipher(decrypted_key)
        return cipher.decrypt(encrypted)

    def _get_cf_params(self, stack_name):
        clf = self._session.client('cloudformation')
        stack = clf.describe_stacks(StackName=stack_name)
        ret = {}
        for output in  stack['Stacks'][0]['Outputs']:
            if output['OutputKey'] == 'vaultBucketName':
                ret['bucket_name'] = output['OutputValue']
            if output['OutputKey'] == 'kmsKeyArn':
                ret['key_arn'] = output['OutputValue']
        return ret

    def store(self, name, data):
        s3cl = self._session.client('s3')
        encrypted = self._encrypt(data)
        s3cl.put_object(Bucket=self._vault_bucket, Body=encrypted['datakey'],
                        ACL='private', Key=self._prefix + name + '.key')
        s3cl.put_object(Bucket=self._vault_bucket, Body=encrypted['ciphertext'],
                        ACL='private', Key=self._prefix + name + '.encrypted')
        return True

    def lookup(self, name):
        s3cl = self._session.client('s3')
        ciphertext = s3cl.get_object(Bucket=self._vault_bucket,
                                     Key=self._prefix + name + '.encrypted')['Body'].read()
        datakey = s3cl.get_object(Bucket=self._vault_bucket,
                                  Key=self._prefix + name + '.key')['Body'].read()
        return self._decrypt(datakey, ciphertext)

    def exists(self, name):
        s3cl = self._session.client('s3')
        try:
            s3cl.head_object(Bucket=self._vault_bucket,
                             Key=self._prefix + name + '.key')
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise

    def delete(self, name):
        s3cl = self._session.client('s3')
        s3cl.delete_object(Bucket=self._vault_bucket, Key=self._prefix + name + '.key')
        s3cl.delete_object(Bucket=self._vault_bucket, Key=self._prefix + name + '.encrypted')
    def all(self):
        s3bucket = self._session.resource('s3').Bucket(self._vault_bucket)
        ret = ""
        for object in s3bucket.objects.filter(Prefix=self._prefix):
            if object.key.endswith(".encrypted"):
                ret = ret + object.key[:-10] + os.linesep
        return ret


def _get_cipher(key):
    ctr = Counter.new(128, initial_value=1337)
    return AES.new(key, AES.MODE_CTR, counter=ctr)
