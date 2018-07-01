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
                }, 
                {
                    "Description": "subnet id", 
                    "OutputKey": "subnetInfraC", 
                    "OutputValue": "subnet-7278372b"
                }, 
                {
                    "Description": "vpc id", 
                    "OutputKey": "VPC", 
                    "OutputValue": "vpc-f3bd9896"
                }, 
                {
                    "Description": "infra security group id", 
                    "OutputKey": "sgInfra", 
                    "OutputValue": "sg-b40077d0"
                }, 
                {
                    "Description": "SSH in security group id", 
                    "OutputKey": "sgSSHFromAnywhere", 
                    "OutputValue": "sg-ab0077cf"
                }
            ], 
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
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::NetworkAclEntry", 
            "Timestamp": "2015-12-31T10:45:44.338Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "infra-aclen-SYVPJD614F0S", 
            "LogicalResourceId": "aclentryAllowAllIngress"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::VPCDHCPOptionsAssociation", 
            "Timestamp": "2015-12-31T10:45:20.090Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "infra-dchpa-F77KZOCMQR6J", 
            "LogicalResourceId": "dchpassoc1"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::DHCPOptions", 
            "Timestamp": "2015-12-31T10:45:15.236Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "dopt-fd964298", 
            "LogicalResourceId": "doptNitorInfra"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::InternetGateway", 
            "Timestamp": "2015-12-31T10:45:15.401Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "igw-e1fd9884", 
            "LogicalResourceId": "igwNitorInfra"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::VPCGatewayAttachment", 
            "Timestamp": "2015-12-31T10:45:36.055Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "infra-igwNi-6QPA0OLZDNWR", 
            "LogicalResourceId": "igwNitorInfraAttachment"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::Route", 
            "Timestamp": "2015-12-31T10:46:03.301Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "infra-route-QROTMX6YW1J9", 
            "LogicalResourceId": "routertbPlubicIGW"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::RouteTable", 
            "Timestamp": "2015-12-31T10:45:23.294Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "rtb-d3eaeab6", 
            "LogicalResourceId": "rtbPublic"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SecurityGroup", 
            "Timestamp": "2015-12-31T10:45:39.499Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "sg-b40077d0", 
            "LogicalResourceId": "sgInfra"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SecurityGroup", 
            "Timestamp": "2015-12-31T10:45:37.459Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "sg-ab0077cf", 
            "LogicalResourceId": "sgSSHFromAnywhere"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "UPDATE_COMPLETE", 
            "ResourceType": "AWS::EC2::Subnet", 
            "Timestamp": "2015-12-31T11:49:09.940Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "subnet-abe2edce", 
            "LogicalResourceId": "subnetInfraA"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "UPDATE_COMPLETE", 
            "ResourceType": "AWS::EC2::Subnet", 
            "Timestamp": "2015-12-31T11:47:37.548Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "subnet-70112607", 
            "LogicalResourceId": "subnetInfraB"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "UPDATE_COMPLETE", 
            "ResourceType": "AWS::EC2::Subnet", 
            "Timestamp": "2015-12-31T11:47:39.033Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "subnet-7278372b", 
            "LogicalResourceId": "subnetInfraC"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SubnetNetworkAclAssociation", 
            "Timestamp": "2015-12-31T10:45:59.447Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "aclassoc-5cac153b", 
            "LogicalResourceId": "subnetacl1"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SubnetNetworkAclAssociation", 
            "Timestamp": "2015-12-31T10:45:59.371Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "aclassoc-5dac153a", 
            "LogicalResourceId": "subnetacl2"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SubnetNetworkAclAssociation", 
            "Timestamp": "2015-12-31T10:46:01.066Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "aclassoc-5aac153d", 
            "LogicalResourceId": "subnetacl3"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SubnetRouteTableAssociation", 
            "Timestamp": "2015-12-31T10:45:57.843Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "rtbassoc-4beb012f", 
            "LogicalResourceId": "subnetroute2"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SubnetRouteTableAssociation", 
            "Timestamp": "2015-12-31T10:45:56.558Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "rtbassoc-49eb012d", 
            "LogicalResourceId": "subnetroute3"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::SubnetRouteTableAssociation", 
            "Timestamp": "2015-12-31T10:45:56.716Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "rtbassoc-4aeb012e", 
            "LogicalResourceId": "subnetroute4"
        }, 
        {
            "StackId": "arn:aws:cloudformation:eu-west-1:832585949989:stack/infra-network/809d77a0-afab-11e5-92de-50faeb52a4d2", 
            "ResourceStatus": "CREATE_COMPLETE", 
            "ResourceType": "AWS::EC2::VPC", 
            "Timestamp": "2015-12-31T10:45:16.068Z", 
            "StackName": "infra-network", 
            "PhysicalResourceId": "vpc-f3bd9896", 
            "LogicalResourceId": "vpcNitorInfra"
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

