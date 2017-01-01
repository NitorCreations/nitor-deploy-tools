import argparse
import os
import sys
from . import aws_infra_util
from . import cf_utils
from . import cf_deploy
from .cf_utils import InstanceInfo

def yaml_to_json():
    parser = argparse.ArgumentParser(description="Convert Nitor CloudFormation yaml to CloudFormation json with some preprosessing")
    parser.add_argument("file", help="File to parse")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    print aws_infra_util.yaml_to_json(args.file)

def json_to_yaml():
    parser = argparse.ArgumentParser(description="Convert CloudFormation json to an approximation of a Nitor CloudFormation yaml with for example scripts externalized")
    parser.add_argument("file", help="File to parse")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    print aws_infra_util.json_to_yaml(args.file)

def read_and_follow():
    parser = argparse.ArgumentParser(description="Read a file and follow the end")
    parser.add_argument("file", help="File to follow")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    cf_utils.read_and_follow(args.file, sys.stdout.write)

def logs_to_cloudwatch():
    parser = argparse.ArgumentParser(description="Read a file and follow and send to cloudwatch")
    parser.add_argument("file", help="File to follow")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    cf_utils.send_logs_to_cloudwatch(args.file)

def signal_cf_status():
    parser = argparse.ArgumentParser(description="Signal cloudformation status")
    parser.add_argument("status", help="Status to indicate: SUCCESS | FAILURE")
    parser.add_argument("-r", "--resource", help="Logical resource name to signal. Looked up for cloudformation tags by default")
    args = parser.parse_args()
    if args.status != "SUCCESS" and args.status != "FAILURE":
        parser.error("Status needs to be SUCCESS or FAILURE")
    cf_utils.signal_status(args.status, resource_name=args.resource)

def associate_eip():
    parser = argparse.ArgumentParser(description="Allocate Elastic IP for into instance")
    parser.add_argument("-i", "--ip", help="Elastic IP to allocate - default is to get paramEip from stack")
    parser.add_argument("-a", "--allocationid", help="Elastic IP allocation id to allocate - default is to get paramEipAllocationId from stack")
    parser.add_argument("-e", "--eipparam", help="Parameter to look up for Elastic IP in the stack - default is paramEip", default="paramEip")
    parser.add_argument("-p", "--allocationidparam", help="Parameter to look up for Elastic IP Allocation ID in the stack - default is paramEipAllocationId", default="paramEipAllocationId")
    args = parser.parse_args()
    cf_utils.associate_eip(eip=args.ip, allocation_id=args.allocationid,
                           eip_param=args.eipparam,
                           allocation_id_param=args.allocationidparam)

def instance_id():
    info = InstanceInfo()
    print info.instance_id

def region():
    info = InstanceInfo()
    print info.region

def stack_name():
    info = InstanceInfo()
    print info.stack_name

def stack_id():
    info = InstanceInfo()
    print info.stack_id

def logical_id():
    info = InstanceInfo()
    print info.logical_id

def cf_region():
    info = InstanceInfo()
    print info.stack_id.split(":")[3]

def update_stack():
    parser = argparse.ArgumentParser(description="Create or update existing CloudFormation stack")
    parser.add_argument("stack_name", help="Name of the stack to create or update")
    parser.add_argument("yaml_template", help="Yaml template to pre-process and use for creation")
    parser.add_argument("region", help="The region to deploy the stack to")
    args = parser.parse_args()
    if not os.path.isfile(args.yaml_template):
        parser.error(args.file + " not found")
    cf_deploy.deploy(args.stack_name, args.yaml_template, args.region)
