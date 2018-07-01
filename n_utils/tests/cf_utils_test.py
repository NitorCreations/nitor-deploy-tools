from n_utils.cf_utils import InstanceInfo, INSTANCE_IDENTITY_URL
from dateutil.parser import parse

class IdentityResp:
    def __init__(self):
        return

    text = """
{
  "privateIp" : "192.168.208.238",
  "devpayProductCodes" : null,
  "marketplaceProductCodes" : [ "aw0evgkw8e5c1q413zgy5pjce" ],
  "version" : "2017-09-30",
  "instanceId" : "i-021614c41980832b8",
  "billingProducts" : null,
  "instanceType" : "m3.large",
  "availabilityZone" : "eu-west-1a",
  "accountId" : "832585949989",
  "kernelId" : null,
  "ramdiskId" : null,
  "architecture" : "x86_64",
  "imageId" : "ami-f8252c12",
  "pendingTime" : "2018-06-26T12:24:28Z",
  "region" : "eu-west-1"
}
"""
class ClientResp:
    def __init__(self):
        return
    def describe_tags(self, Filters=None):
        assert Filters[0]['Name'] == 'resource-id'
        assert Filters[0]['Values'] == ['i-021614c41980832b8']
        return {"Tags": [{"Key": 'aws:cloudformation:stack-name', "Value": "test-stack"}]}
    def describe_stacks(self, StackName=None):
        assert StackName == "test-stack"
        return {
    "Stacks": [
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "Description": "Nitor infra network stack", 
            "Tags": [], 
            "Outputs": [
                {
                    "Description": "subnet id", 
                    "OutputKey": "subnetInfraA", 
                    "OutputValue": "subnet-abe2edce"
                }, 
                {
                    "Description": "subnet id", 
                    "OutputKey": "subnetInfraB", 
                    "OutputValue": "subnet-70112607"
                }],
            "EnableTerminationProtection": False, 
            "CreationTime": parse("2015-12-31T10:44:43.689Z"), 
            "StackName": "infra-network", 
            "NotificationARNs": [], 
            "StackStatus": "UPDATE_ROLLBACK_COMPLETE", 
            "LastUpdatedTime": parse("2015-12-31T13:39:48.260Z"), 
            "DisableRollback": False, 
            "RollbackConfiguration": {}
        }
    ]
}
    def describe_stack_resources(self, StackName=None):
        assert StackName == "test-stack"
        return {
    "StackResources": [
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::NetworkAcl", 
            "Timestamp": "2015-12-31T10:45:24.071Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "acl-f94c779c", 
            "LogicalResourceId": "aclNitorInfra"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::NetworkAclEntry", 
            "Timestamp": "2015-12-31T10:45:45.723Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "infra-aclen-4YIM1ZP45OYX", 
            "LogicalResourceId": "aclentryAllowAllEgress"
        }
    ]
}


def test_instance_info(mocker):
    boto3 = mocker.patch('n_utils.cf_utils.boto3')
    boto3.client.return_value = ClientResp() 
    retry = mocker.patch('n_utils.cf_utils.get_retry')
    retry.return_value = IdentityResp() 
    is_ec2 = mocker.patch('n_utils.cf_utils.is_ec2')
    is_ec2.return_value = True
    wait_net_service = mocker.patch('n_utils.cf_utils.wait_net_service')
    wait_net_service.return_value = True
    info = InstanceInfo()
    assert info.instance_id() == "i-021614c41980832b8"
    assert info.region() == "eu-west-1"
    assert info.stack_name() == "test-stack"
    retry.assert_called_with(INSTANCE_IDENTITY_URL)
    wait_net_service.assert_called_with("169.254.169.254", 80, 120)

