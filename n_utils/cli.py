# Copyright 2016-2017 Nitor Creations Oy
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

""" Command line tools for nitor-deploy-tools
"""

import argparse
import json
import os
import sys
import time

from . import aws_infra_util
from . import cf_bootstrap
from . import cf_deploy
from . import cf_utils
from .cf_utils import InstanceInfo
from .log_events import CloudWatchLogs, CloudFormationEvents
from .maven_utils import add_server


def list_file_to_json():
    """ Convert a file with an entry on each line to a json document with
    a single element (name as argument) containg file rows as  list.
    """
    parser = argparse.ArgumentParser(description="Ouput a file with one item" +\
                                                 " per line as a json object")
    parser.add_argument("arrayname", help="The name in the json object given" +\
                                          "to the array")
    parser.add_argument("file", help="The file to parse")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    content = [line.rstrip('\n') for line in open(args.file)]
    json.dump({args.arrayname : content}, sys.stdout)

def create_userid_list():
    """Ouput arguments as a json object containing one array named 'Add'. Used
    in scripts used to share AWS AMI images with other AWS accounts and regions
    """
    parser = argparse.ArgumentParser(description="Ouput arguments as a " +\
                                                 "json object containing one" +\
                                                 " array named 'Add'. Used " +\
                                                 "in scripts used to share " +\
                                                 "AWS AMI images with other " +\
                                                 "AWS accounts and regions")
    parser.add_argument("user_ids", help="User ids to dump", nargs="+")
    args = parser.parse_args()
    ret = {"Add": []}
    for user_id in args.user_ids:
        ret['Add'].append({"UserId": user_id})
    json.dump(ret, sys.stdout)

def add_deployer_server():
    """Add a server into a maven configuration file. Password is taken from the
    environment variable 'DEPLOYER_PASSWORD'
    """
    parser = argparse.ArgumentParser(description="Add a server into a maven" +\
                                                 " configuration file. " +\
                                                 "Password is taken from the" +\
                                                 " environment variable " +\
                                                 "'DEPLOYER_PASSWORD'")
    parser.add_argument("file", help="The file to modify")
    parser.add_argument("username", help="The username to access the server.")
    parser.add_argument("--id", help="Optional id for the server. Default is" +\
                                     " deploy. One server with this id is " +\
                                     "added and another with '-release' " +\
                                     "appended", default="deploy")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    add_server(args.file, args.id, args.username)
    add_server(args.file, args.id + "-release", args.username)

def get_userdata():
    """Get userdata defined for an instance into a file
    """
    parser = argparse.ArgumentParser(description="Get userdata defined for " +\
                                                 "an instance into a file")
    parser.add_argument("file", help="File to write userdata into")
    args = parser.parse_args()
    dirname = os.path.dirname(args.file)
    if dirname:
        if os.path.isfile(dirname):
            parser.error(dirname + " exists and is a file")
        elif not os.path.isdir(dirname):
            os.makedirs(dirname)
    cf_utils.get_userdata(args.file)
    return

def get_account_id():
    """Get current account id. Either from instance metadata or current cli
    configuration.
    """
    print cf_utils.resolve_account()

def yaml_to_json():
    """"Convert Nitor CloudFormation yaml to CloudFormation json with some
    preprosessing
    """
    parser = argparse.ArgumentParser(description="Convert Nitor" +\
                                                 "CloudFormation yaml to " +\
                                                 "CloudFormation json with " +\
                                                 "some preprosessing")
    parser.add_argument("file", help="File to parse")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    print aws_infra_util.yaml_to_json(args.file)

def json_to_yaml():
    """Convert CloudFormation json to an approximation of a Nitor CloudFormation
    yaml with for example scripts externalized
    """
    parser = argparse.ArgumentParser(description="Convert CloudFormation " +\
                                                 "json to an approximation " +\
                                                 "of a Nitor CloudFormation " +\
                                                 "yaml with for example " +\
                                                 "scripts externalized")
    parser.add_argument("file", help="File to parse")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    print aws_infra_util.json_to_yaml(args.file)

def read_and_follow():
    """Read and print a file and keep following the end for new data
    """
    parser = argparse.ArgumentParser(description="Read and print a file and" +\
                                                 " keep following the end " +\
                                                 "for new data")
    parser.add_argument("file", help="File to follow")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    cf_utils.read_and_follow(args.file, sys.stdout.write)

def logs_to_cloudwatch():
    """Read a file and send rows to cloudwatch and keep following the end for
    new data
    """
    parser = argparse.ArgumentParser(description="Read a file and send rows " +\
                                                 "to cloudwatch and keep " +\
                                                 "following the end for new " +\
                                                 "data")
    parser.add_argument("file", help="File to follow")
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    cf_utils.send_logs_to_cloudwatch(args.file)

def signal_cf_status():
    """Signal CloudFormation status to a logical resource in CloudFormation
    that is either given on the command line or resolved from CloudFormation
    tags
    """
    parser = argparse.ArgumentParser(description="Signal CloudFormation " +\
                                                 "status to a logical " +\
                                                 "resource in CloudFormation" +\
                                                 " that is either given on " +\
                                                 "the command line or " +\
                                                 "resolved from " +\
                                                 "CloudFormation tags")
    parser.add_argument("status", help="Status to indicate: SUCCESS | FAILURE")
    parser.add_argument("-r", "--resource", help="Logical resource name to" +\
                                                 " signal. Looked up for" +\
                                                 "cloudformation tags by" +\
                                                 "default")
    args = parser.parse_args()
    if args.status != "SUCCESS" and args.status != "FAILURE":
        parser.error("Status needs to be SUCCESS or FAILURE")
    cf_utils.signal_status(args.status, resource_name=args.resource)

def associate_eip():
    """Associate an Elastic IP for the instance
    """
    parser = argparse.ArgumentParser(description="Associate an Elastic IP " +\
                                                 "for the instance")
    parser.add_argument("-i", "--ip", help="Elastic IP to allocate - default" +\
                                           " is to get paramEip from stack")
    parser.add_argument("-a", "--allocationid", help="Elastic IP allocation " +\
                                                     "id to allocate - " +\
                                                     "default is to get " +\
                                                     "paramEipAllocationId " +\
                                                     "from stack")
    parser.add_argument("-e", "--eipparam", help="Parameter to look up for " +\
                                                 "Elastic IP in the stack - " +\
                                                 "default is paramEip",
                        default="paramEip")
    parser.add_argument("-p", "--allocationidparam", help="Parameter to look" +\
                                                          " up for Elastic " +\
                                                          "IP Allocation ID " +\
                                                          "in the stack - " +\
                                                          "default is " +\
                                                          "paramEipAllocatio" +\
                                                          "nId",
                        default="paramEipAllocationId")
    args = parser.parse_args()
    cf_utils.associate_eip(eip=args.ip, allocation_id=args.allocationid,
                           eip_param=args.eipparam,
                           allocation_id_param=args.allocationidparam)

def instance_id():
    """ Get id for instance
    """
    info = InstanceInfo()
    print info.instance_id

def region():
    """ Get region for instance
    """
    info = InstanceInfo()
    print info.region

def stack_name():
    """ Get name of the stack that created this instance
    """
    info = InstanceInfo()
    print info.stack_name

def stack_id():
    """ Get id of the stack the creted this instance
    """
    info = InstanceInfo()
    print info.stack_id

def logical_id():
    """ Get the logical id that is expecting a signal from this instance
    """
    info = InstanceInfo()
    print info.logical_id

def cf_region():
    """ Get region of the stack that created this instance
    """
    info = InstanceInfo()
    print info.stack_id.split(":")[3]

def update_stack():
    """ Create or update existing CloudFormation stack
    """
    parser = argparse.ArgumentParser(description="Create or update existing " +\
                                                 "CloudFormation stack")
    parser.add_argument("stack_name", help="Name of the stack to create or " +\
                                            "update")
    parser.add_argument("yaml_template", help="Yaml template to pre-process " +\
                                              "and use for creation")
    parser.add_argument("region", help="The region to deploy the stack to")
    args = parser.parse_args()
    if not os.path.isfile(args.yaml_template):
        parser.error(args.yaml_template + " not found")
    cf_deploy.deploy(args.stack_name, args.yaml_template, args.region)
    return

def delete_stack():
    """Create or update existing CloudFormation stack
    """
    parser = argparse.ArgumentParser(description="Create or update existing " +\
                                                 "CloudFormation stack")
    parser.add_argument("stack_name", help="Name of the stack to delete")
    parser.add_argument("region", help="The region to delete the stack from")
    args = parser.parse_args()
    cf_deploy.delete(args.stack_name, args.region)
    return

def tail_stack_logs():
    """Tail logs from the log group of a cloudformation stack
    """
    parser = argparse.ArgumentParser(description="Tail logs from the log " +\
                                                 "group of a cloudformation " +\
                                                 "stack")
    parser.add_argument("stack_name", help="Name of the stack to watch logs " +\
                                           "for")
    parser.add_argument("-s", "--start", help="Start time in seconds since" +\
                                              "epoc")
    args = parser.parse_args()
    cwlogs = CloudWatchLogs(args.stack_name, start_time=args.start)
    cwlogs.start()
    cfevents = CloudFormationEvents(args.stack_name, start_time=args.start)
    cfevents.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print 'Closing...'
            cwlogs.stop()
            cfevents.stop()
            return

def resolve_include():
    """Find a file from the first of the defined include paths
    """
    parser = argparse.ArgumentParser(description="Find a file from the first" +\
                                                " of the defined include paths")
    parser.add_argument("file", help="The file to find")
    args = parser.parse_args()
    inc_file = aws_infra_util.find_include(args.file)
    if not inc_file:
        parser.error("Include " + args.file + " not found on include paths " +\
                     str(aws_infra_util.include_dirs))
    print inc_file

def assume_role():
    """Assume a defined role. Prints out environment variables
    to be eval'd to current context for use:
    eval $(assume-role 'arn:aws:iam::43243246645:role/DeployRole')"""
    parser = argparse.ArgumentParser(description="Assume a defined role. " +\
                                                 "Prints out environment " +\
                                                 "variables to be eval'd " +\
                                                 "to current context for " +\
                                                 "use:\neval $(assume-role " +\
                                                 "'arn:aws:iam::43243246645:" +\
                                                 "role/DeployRole')")
    parser.add_argument("role_arn", help="The ARN of the role to assume")
    args = parser.parse_args()
    creds = cf_utils.assume_role(args.role_arn)
    print "AWS_ACCESS_KEY_ID=\"" + creds['AccessKeyId'] + "\""
    print "AWS_SECRET_ACCESS_KEY=\"" + creds['SecretAccessKey'] + "\""
    print "AWS_SESSION_TOKEN=\"" + creds['SessionToken'] + "\""
    print "export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN"

def get_parameter():
    """Get a parameter value from the stack
    """
    parser = argparse.ArgumentParser(description="Get a parameter value from" +\
                                                 " the stack")
    parser.add_argument("parameter", help="The name of the parameter to print")
    args = parser.parse_args()
    info = InstanceInfo()
    print info.stack_data(args.parameter)

def clean_snapshots():
    """Clean snapshots that are older than a number of days (30 by default) and
    have one of specified tag values
    """
    parser = argparse.ArgumentParser(description="Clean snapshots that are " +\
                                                 "older than a number of " +\
                                                 "days (30 by default) and " +\
                                                 "have one of specified tag " +\
                                                 "values")
    parser.add_argument("-r", "--region", help="The region to delete " +\
                                               "snapshots from. Can also be " +\
                                               "set with env variable " +\
                                               "AWS_DEFAULT_REGION or is " +\
                                               "gotten from instance " +\
                                               "metadata as a last resort")
    parser.add_argument("-d", "--days", help="The number of days that is the" +\
                                             "minimum age for snapshots to " +\
                                             "be deleted", type=int, default=30)
    parser.add_argument("tags", help="The tag values to select deleted " +\
                                     "snapshots", nargs="+")
    args = parser.parse_args()
    if args.region:
        os.environ['AWS_DEFAULT_REGION'] = args.region
    cf_utils.clean_snapshots(args.days, args.tags)

def setup_cli():
    """Setup the command line environment to define an aws cli profile with
    the given name and credentials. If an identically named profile exists,
    it will not be overwritten.
    """
    parser = argparse.ArgumentParser(description="Setup the command line " +\
                                                 "environment to define an " +\
                                                 "aws cli profile with the " +\
                                                 "given name and credentials" +\
                                                 ". If an identically named" +\
                                                 " profile exists, it will " +\
                                                 "not be overwritten.")
    parser.add_argument("-n", "--name", help="Name for the profile to create")
    parser.add_argument("-k", "--key-id", help="Key id for the profile")
    parser.add_argument("-s", "--secret", help="Secret to set for the profile")
    parser.add_argument("-r", "--region", help="Default region for the profile")
    args = parser.parse_args()
    cf_bootstrap.setup_cli(**vars(args))

def setup_networks():
    """Setup a VPC and a private and public network in each availability zone.
    """
    parser = argparse.ArgumentParser(description="Setup a VPC and a private " +\
                                                 "and public network in each" +\
                                                 " availability zone.")
    parser.add_argument("-y", "--yes", help="Answer yes and go with defaults" +\
                                            " for all questions",
                        action="store_true")
    parser.add_argument("-n", "--name", help="Name for the infra network " +\
                                             "to create")
    parser.add_argument("-v", "--vpc-cidr", help="CIDR for the VPC")
    parser.add_argument("-p", "--subnet-prefixlen", help="The lenght of the " +\
                                                         "bitmask for " +\
                                                         "created subnets",
                        type=int)
    parser.add_argument("-b", "--subnet-base", help="Base address for " + \
                                                    "subnets within the VPC")
    args = parser.parse_args()
    print cf_bootstrap.setup_networks(**vars(args))
