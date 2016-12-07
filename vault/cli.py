from vault import Vault
import argparse
import os
import boto3
import sys
import requests
import json
from requests.exceptions import ConnectionError

def main():
    parser = argparse.ArgumentParser(description="Store and lookup locally encrypted data stored in S3")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-s', '--store', help="Name of element to store. Optionally read from file name", nargs='?', default="")
    action.add_argument('-l', '--lookup', help="Name of element to lookup")
    action.add_argument('-i', '--init', action='store_true', help="Initializes a kms key and an s3 bucket with some roles for reading and writing on a fresh account via CloudFormation. Means that the account used has to have rights to create the resources")
    action.add_argument('-d', '--delete', help="Name of element to delete")
    data = parser.add_mutually_exclusive_group(required=False)
    data.add_argument('-v', '--value', help="Value to store")
    data.add_argument('-f', '--file', help="File to store. If no -s argument given, the name of the file is used as the default name. Give - for stdin")
    parser.add_argument('-o', "--outfile", help="The file to write the data to")
    parser.add_argument('-p', '--prefix', help="Optional prefix to store value under. 'default/' by default")
    parser.add_argument('--vaultstack', help="Optional CloudFormation stack to lookup key and bucket. 'vault' by default")
    parser.add_argument('-b', '--bucket', help="Override the bucket name either for initialization or storing and looking up values")
    parser.add_argument('-k', '--key-arn',  help="Override the KMS key arn for storinig or looking up")
    parser.add_argument('--id', help="Give an IAM access key id to override those defined by environent")
    parser.add_argument('--secret', help="Give an IAM secret access key to override those defined by environent")
    parser.add_argument('-r', '--region', help="Give a region for the stack and bucket")
    args = parser.parse_args()
    if args.store and not (args.value or args.file):
        parser.error("--store requires --value or --file")
    if not args.store and not args.lookup and not args.init and not args.file and not args.delete:
        parser.error("--store requires name or a --file argument to get name to store")
    elif not args.store and not args.lookup and not args.init and not args.delete:
        if args.file == "-":
            parser.error("--store requires a name for stdin")
        else:
            args.store = os.path.basename(args.file)
            data = open(args.file, 'rb').read()
    elif args.store:
        if args.value:
            data = args.value.encode()
        elif args.file == "-":
            data = sys.stdin.read()
        else:
            data = open(args.file, 'rb').read()
    if not args.vaultstack:
        if "VAULT_STACK" in os.environ:
            args.vaultstack = os.environ["VAULT_STACK"]
        else:
            args.vaultstack = "vault"

    if not args.bucket and "VAULT_BUCKET" in os.environ:
        args.bucket = os.environ["VAULT_BUCKET"]

    if not args.prefix and "VAULT_PREFIX" in os.environ:
        args.prefix = os.environ["VAULT_PREFIX"]
    elif not args.prefix:
        args.prefix = "default/"

    instance_data = None
    # Try to get region from instance metadata if not otherwise specified
    if not args.region and not "AWS_DEFAULT_REGION" in os.environ:
        try:
            response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
            instance_data = json.loads(response.text)
            args.region = instance_data['region']
        except ConnectionError:
            # no-op
            args.region = ""

    if args.region:
        os.environ['AWS_DEFAULT_REGION'] = args.region

    if not args.init:
        vlt = Vault(vault_stack=args.vaultstack, vault_key=args.key_arn,
            vault_bucket=args.bucket, vault_iam_id=args.id,
            vault_iam_secret=args.secret, vault_prefix=args.prefix)
        if args.store:
            vlt.store(args.store, data)
        elif args.delete:
            vlt.delete(args.delete)
        else:
            data = vlt.lookup(args.lookup)
            if args.outfile and not args.outfile == "-":
                with open(args.outfile, 'w') as f:
                    f.write(data)
            else:
                sys.stdout.write(data)
    else:
        if not args.bucket:
            try:
                if not instance_data:
                    response = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document')
                    instance_data = json.loads(response.text)
                account_id = instance_data['accountId']
                args.bucket = "vault-" + account_id
            except ConnectionError:
                iam = boto3.client("iam")
                arn = iam.get_user()['User']['Arn']
                args.bucket = "vault-" + arn.split(':')[4]
        clf = boto3.client("cloudformation")
        try:
            clf.describe_stacks(StackName=args.vaultstack)
            print "Vault stack '" + args.vaultstack + "' already initialized"
        except:
            template = '{"Parameters": {"paramBucketName": {"Description": "Name of the vault bucket", "Type": "String", "Default": "nitor-core-vault"}}, "Resources": {"kmsKey": {"Type": "AWS::KMS::Key", "Properties": {"Description": "Key for encrypting / decrypting secrets", "KeyPolicy": {"Version": "2012-10-17", "Id": "key-default-2", "Statement": [{"Sid": "allowAdministration", "Effect": "Allow", "Principal": {"AWS": {"Fn::Join": ["", ["arn:aws:iam::", {"Ref": "AWS::AccountId"}, ":root"]]}}, "Action": ["kms:*"], "Resource": "*"}]}}}, "vaultBucket": {"Type": "AWS::S3::Bucket", "Properties": {"BucketName": {"Ref": "paramBucketName"}}}, "resourceDecryptRole": {"Type": "AWS::IAM::Role", "Properties": {"AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}, "Path": "/"}}, "resourceEncryptRole": {"Type": "AWS::IAM::Role", "Properties": {"AssumeRolePolicyDocument": {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]}, "Path": "/"}}, "iamPolicyDecrypt": {"Type": "AWS::IAM::Policy", "Properties": {"PolicyName": "AllowVaultDecrypt", "Roles": [{"Ref": "resourceDecryptRole"}], "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Sid": "getVault", "Effect": "Allow", "Action": "s3:GetObject", "Resource": {"Fn::Join": ["", ["arn:aws:s3:::", {"Ref": "paramBucketName"}, "/*"]]}}, {"Sid": "allowDecrypt", "Effect": "Allow", "Action": ["kms:Decrypt"], "Resource": {"Fn::GetAtt": ["kmsKey", "Arn"]}}]}}}, "iamPolicyEncrypt": {"Type": "AWS::IAM::Policy", "Properties": {"PolicyName": "AllowVaultDecrypt", "Roles": [{"Ref": "resourceEncryptRole"}], "PolicyDocument": {"Version": "2012-10-17", "Statement": [{"Sid": "putVault", "Effect": "Allow", "Action": ["s3:GetObject", "s3:PutObject"], "Resource": {"Fn::Join": ["", ["arn:aws:s3:::", {"Ref": "paramBucketName"}, "/*"]]}}, {"Sid": "allowDecrypt", "Effect": "Allow", "Action": ["kms:Decrypt", "kms:Encrypt"], "Resource": {"Fn::GetAtt": ["kmsKey", "Arn"]}}]}}}}, "Outputs": {"kmsKeyArn": {"Description": "KMS key Arn", "Value": {"Fn::GetAtt": ["kmsKey", "Arn"]}}, "vaultBucketName": {"Description": "Vault Bucket", "Value": {"Ref": "vaultBucket"}}, "decryptPolicy": {"Description": "The policy for decrypting", "Value": {"Ref": "iamPolicyDecrypt"}}, "encryptPolicy": {"Description": "The policy for decrypting", "Value": {"Ref": "iamPolicyEncrypt"}}}}'
            params = {}
            params['ParameterKey'] = "paramBucketName"
            params['ParameterValue'] = args.bucket
            clf.create_stack(StackName=args.vaultstack, TemplateBody=template,
                             Parameters=[params], Capabilities=['CAPABILITY_IAM'])
