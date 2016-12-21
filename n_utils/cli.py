import argparse
import aws_infra_util
import cf_utils
import os.path
import sys

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
    parser.add_argument("-r", "--resource", help="Logical resource name to signal. resourceAsg by default", default="resourceAsg")
    args = parser.parse_args()
    if args.status != "SUCCESS" and args.status != "FAILURE":
        parser.error("Status needs to be SUCCESS or FAILURE")
    cf_utils.signal_status(args.status, resource_name=args.resource)

def associate_eip():
    parser = argparse.ArgumentParser(description="Allocate Elastic IP for into instance")
    parser.add_argument("-i", "--ip", help="Elastic IP to allocate - default is to get paramEip from stack")
    parser.add_argument("-a", "--allocationid", help="Elastic IP allocation id to allocate - default is to get paramEipAllocationId from stack")
    parser.add_argument("-e", "--eipparam", help="Parameter to look up for Elastic IP in the stack - default is paramEip",
                        default="eipParam")
    parser.add_argument("-p", "--allocationidparam", help="Parameter to look up for Elastic IP Allocation ID in the stack - default is paramEipAllocationId",
                        default="paramEipAllocationId")
    args = parser.parse_args()
    cf_utils.associate_eip(eip=args.ip, allocation_id=args.allocationid,
                           eip_param=args.eipparam,
                           allocation_id_param=args.allocationidparam)
