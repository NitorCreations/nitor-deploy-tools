from __future__ import print_function
import boto3
from time import time, sleep

ASSUME_ROLE_POLICY="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::%(account_id)s:root"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"""
def create_account(email, account_name, role_name="OrganizationAccountAccessRole",
                   trusted_role="TrustedAccountAccessRole"
                   access_to_billing=True, trusted_account=None):
    if access_to_billing:
        access = "ALLOW"
    else:
        access = "DENY"
    timeout = 300
    client = boto3.client('organizations')
    response = client.create_account(Email=email, AccountName=account_name,
                                     RoleName=role_name, IamUserAccessToBilling=access)
    if 'CreateAccountStatus' in response and 'Id' in response['CreateAccountStatus']:
        create_account_id = response['CreateAccountStatus']['Id']
        startTime = time()
        status = response['CreateAccountStatus']['State']
        while time() - startTime < timeout and not status == "SUCCEEDED":
            if response['CreateAccountStatus']['State'] == "FAILED":
                raise Exception("Account creation failed: " + response['CreateAccountStatus']['FailureReason'])
            print ("Waiting for account creation to finish")
            sleep(3)
            response = client.describe_create_account_status(CreateAccountRequestId=create_account_id)
            status = response['CreateAccountStatus']['State']
        if time() - startTime > timeout and not status == "SUCCEEDED":
            raise Exception("Timed out waiting to create account " + response['CreateAccountStatus']['State'])
        account_id = response['CreateAccountStatus']['AccountId']
    if trusted_account:
        add_managed_policy_to_manage(account_id)
        attach_managed_policy_to_manage(account_id)
        assume_role(role_name)
        client = boto3.client("iam")
        response = client.create_role(RoleName=trusted_role,
                                      AssumeRolePolicyDocument=ASSUME_ROLE_POLICY % {account_id=trusted_account}
                                      Description="Admin role for account "+ trusted_account)
        client.put_role_policy("*/*")
        assume_role(trusted_account)
        add_managed_policy_to_manage(account_id)
        

def add_managed_policy_to_manage(target_account):
    ## Todo
    return