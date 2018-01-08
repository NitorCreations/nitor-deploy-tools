#!/usr/bin/env python

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

""" Utilities to bootsrap AWS accounts into use with nitor-deploy-tools
"""

import collections
import os
import random
import re
import shutil
import subprocess
import stat
import sys
from copy import deepcopy

import argparse
import argcomplete
from argcomplete import split_line
from argcomplete.completers import ChoicesCompleter, FilesCompleter

import boto3
import ipaddr
from . import cf_deploy
from .aws_infra_util import find_include, find_all_includes, yaml_load, yaml_save
from awscli.customizations.configure.writer import ConfigFileWriter
from .aws_infra_util import find_include, yaml_load, json_save_small, yaml_save
from .cf_utils import has_output_selector, select_stacks

def enum(**enums):
    return type('Enum', (), enums)

BRANCH_MODES = enum(SINGLE_STACK='single', MULTI_STACK='multi')

def create_stack():
    """ Create a stack from a template
    """
    parser = argparse.ArgumentParser(description=create_stack.__doc__, add_help=False)
    parser.add_argument("template").completer = ChoicesCompleter(list_templates())
    parser.add_argument("-h", "--help", action='store_true')
    parser.add_argument("-y", "--yes", action='store_true',
                        help='Answer yes or use default to all questions')
    if "_ARGCOMPLETE" in os.environ:
        args = argcomplete.split_line(os.environ['COMP_LINE'],
                                      os.environ['COMP_POINT'])[3]
        if len(args) >= 2:
            template = args[1]
            template_yaml = load_template(template)
            if template_yaml and "ContextClass" in template_yaml:
                context = load_class(template_yaml["ContextClass"])()
                context.add_context_arguments(parser)
    argcomplete.autocomplete(parser)
    args, unknown = parser.parse_known_args()
    parser = argparse.ArgumentParser(description=create_stack.__doc__)
    parser.add_argument("template").completer = ChoicesCompleter(list_templates())
    parser.add_argument("-y", "--yes", action='store_true',
                        help='Answer yes or use default to all questions')
    if args.template:
        template_yaml = load_template(args.template)
        if "ContextClass" in template_yaml:
            context = load_class(template_yaml["ContextClass"])()
            context.add_context_arguments(parser)
        template_yaml.pop("ContextClass", None)
    args = parser.parse_args()
    context.resolve_parameters(args)
    context.set_template(template_yaml)
    if context.write(yes=args.yes):
        subprocess.check_call(["ndt", "print-create-instructions",
                               context.component_name, context.stack_name])
    return

def load_template(template):
    file_name = find_include("creatable-templates/" + template + ".yaml")
    if file_name:
        return yaml_load(open(file_name))
    else:
        return None

def load_class(name):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def list_templates():
    ret = []
    files = find_all_includes("creatable-templates/*.yaml")
    for next_file in files:
        next_name = os.path.basename(next_file)[:-5]
        if not next_name in ret:
            ret.append(next_name)
    return ret

def has_entry(prefix, name, file_name):
    if not os.path.isfile(file_name):
        return False
    with open(file_name, "r") as config:
        for line in config.readlines():
            if "[" + prefix + name + "]" == line.strip():
                return True
    return False

def setup_cli(name=None, key_id=None, secret=None, region=None):
    if name is None:
        name = raw_input("Profile name: ")
    home_dir = os.path.expanduser("~")
    config_file = os.path.join(home_dir, ".aws", "config")
    credentials_file = os.path.join(home_dir, ".aws", "credentials")
    if has_entry("profile ", name, config_file) or \
       has_entry("", name, credentials_file):
        print "Profile " + name + " already exists. Not overwriting."
        return
    if key_id is None:
        key_id = raw_input("Key ID: ")
    if secret is None:
        secret = raw_input("Key secret: ")
    if region is None:
        region = raw_input("Default region: ")
    writer = ConfigFileWriter()
    config_values = {
        "__section__": "profile " + name,
        "output": "json",
        "region": region
        }
    credentials_values = {
        "__section__": name,
        "aws_access_key_id": key_id,
        "aws_secret_access_key": secret
        }
    writer.update_config(config_values, config_file)
    writer.update_config(credentials_values, credentials_file)
    home_bin = credentials_file = os.path.join(home_dir, "bin")
    if not os.path.isdir(home_bin):
        os.makedirs(home_bin)
    source_file = os.path.join(home_bin, name)
    with open(source_file, "w") as source_script:
        source_script.write('#!/bin/bash\n\n')
        source_script.write('export AWS_DEFAULT_REGION=')
        source_script.write(region + ' AWS_PROFILE=' + name)
        source_script.write(' AWS_DEFAULT_PROFILE=' + name + "\n")
    os.chmod(source_file, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    os.environ['AWS_PROFILE'] = name
    os.environ['AWS_DEFAULT_PROFILE'] = name
    os.environ['AWS_DEFAULT_REGION'] = region

def _append_cidr_param(public, letter, cidr, params):
    if public:
        cidr_param = "paramPub" + letter + "Cidr"
        description = "Public Subnet " + letter + " CIDR block"
    else:
        cidr_param = "paramPriv" + letter + "Cidr"
        description = "Private Subnet " + letter + " CIDR block"
    params.update({cidr_param: {
        "Description": description,
        "Type": "String",
        "Default": cidr
    }})

def _append_network_resources(public, letter, resources, availability_zone):
    if public:
        subnet_resource = "resourcePubSubnetA"
        route_table_assoc = "resourcePubSubnetRouteTableAssocA"
        cidr_param = "paramPub"  + letter + "Cidr"
        db_subnet = "resourcePubSubnetGroup"
    else:
        subnet_resource = "resourcePrivSubnetA"
        route_table_assoc = "resourcePrivSubnetRouteTableAssocA"
        cidr_param = "paramPriv"  + letter + "Cidr"
        route_table = "resourcePrivRouteTableA"
        db_subnet = "resourcePrivSubnetGroup"

    subnet_to_create = subnet_resource[:-1] + letter

    subnet_res_dict = deepcopy(resources[subnet_resource])
    subnet_res_dict['Properties']['CidrBlock']['Ref'] = cidr_param
    subnet_res_dict['Properties']['AvailabilityZone'] = availability_zone
    subnet_res_dict['Properties']['Tags'][0]['Value']['Fn::Join'][1][1] += \
        availability_zone
    resources.update({subnet_to_create: subnet_res_dict})
    if not public:
        route_table_dict = deepcopy(resources[route_table])
        route_table_dict['Properties']['Tags'][0]['Value']['Fn::Join'][1][1] = \
            " private route table " + letter
        resources.update({route_table[:-1] + letter: route_table_dict})
    route_table_assoc_dict = deepcopy(resources[route_table_assoc])
    if not public:
        route_table_assoc_dict['Properties']['RouteTableId']['Ref'] = \
            route_table[:-1] + letter
    route_table_assoc_dict['Properties']['SubnetId']['Ref'] = \
        subnet_to_create
    resources.update({route_table_assoc[:-1] + letter: route_table_assoc_dict})

    resources[db_subnet]['Properties']['SubnetIds'].append({"Ref": subnet_to_create})

def _get_network_yaml(network, subnet_prefixlen, subnet_base, network_yaml):
    subnet_bits = 32 - subnet_prefixlen
    subnet_size = 2 ** subnet_bits
    ec2 = boto3.client("ec2")
    az_response = ec2.describe_availability_zones()
    last_subnet = subnet_base  - subnet_size
    az_names = sorted([az_data['ZoneName'] for az_data in \
               az_response['AvailabilityZones']])
    network_yaml['Parameters']['paramVPCCidr']['Default'] = str(network)
    for az_name in az_names:
        zone_letter = az_name[-1:]
        zone_upper_letter = zone_letter.upper()
        last_subnet += subnet_size
        private_subnet_addr = last_subnet + (len(az_names) * subnet_size)
        subnet = ipaddr.IPv4Network(str(last_subnet) + "/" + str(subnet_prefixlen))
        private_subnet = ipaddr.IPv4Network(str(private_subnet_addr) + "/" + \
                                            str(subnet_prefixlen))
        if zone_letter == 'a':
            network_yaml['Parameters']['paramPubACidr']['Default'] = \
                str(subnet)
            network_yaml['Parameters']['paramPrivACidr']['Default'] = \
                str(private_subnet)
            network_yaml['Resources']['resourcePubSubnetA']['Properties']\
                ['AvailabilityZone'] = az_name
            network_yaml['Resources']['resourcePrivSubnetA']['Properties']\
                ['AvailabilityZone'] = az_name
        else:
            _append_cidr_param(True, zone_upper_letter, str(subnet),
                               network_yaml['Parameters'])
            _append_cidr_param(False, zone_upper_letter, str(private_subnet),
                               network_yaml['Parameters'])
            _append_network_resources(True, zone_upper_letter,
                                      network_yaml['Resources'], az_name)
            _append_network_resources(False, zone_upper_letter,
                                      network_yaml['Resources'], az_name)
            network_yaml['Outputs']['subnetInfra' + zone_upper_letter] = {
                "Description": "Public Subnet " + zone_upper_letter,
                "Value": {"Ref": "resourcePubSubnet" + zone_upper_letter},
                "Export": {"Name": {"Fn::Join": [":", [{"Ref": "AWS::StackName"},
                                                       "publicSubnet" + zone_upper_letter]]}}
            }
            network_yaml['Outputs']['subnetPrivInfra' + zone_upper_letter] = {
                "Description": "Private Subnet " + zone_upper_letter,
                "Value": {"Ref": "resourcePrivSubnet" + zone_upper_letter},
                "Export": {"Name": {"Fn::Join": [":", [{"Ref": "AWS::StackName"},
                                                       "privateSubnet" + zone_upper_letter]]}}
            }
    return network_yaml

def _get_include_yaml(name, network_yaml, include_data):
    for output_name in network_yaml['Outputs']:
        if output_name == "VPCCIDR":
            include_data['paramVPCCidr'] = {
                "Description": "VPC Cidr",
                "Type": "String",
                "Default": {
                    "StackRef": {
                        "region": {"Ref": "AWS::Region"},
                        "stackName": name,
                        "paramName": output_name}
                }
            }
        elif output_name == "VPC":
            include_data['paramVPCId'] = {
                "Description": "Infra subnet A",
                "Type": "AWS::EC2::VPC::Id",
                "Default": {
                    "StackRef": {
                        "region": {"Ref": "AWS::Region"},
                        "stackName": name,
                        "paramName": output_name}
                }
            }
        elif output_name == "publicSubnetGroup":
            include_data['paramPublicSubnetGroup'] = {
                "Description": "Public subnet group",
                "Type": "String",
                "Default": {
                    "StackRef": {
                        "region": {"Ref": "AWS::Region"},
                        "stackName": name,
                        "paramName": output_name}
                }
            }
        elif output_name == "privateSubnetGroup":
            include_data['paramPrivateSubnetGroup'] = {
                "Description": "Private subnet group",
                "Type": "String",
                "Default": {
                    "StackRef": {
                        "region": {"Ref": "AWS::Region"},
                        "stackName": name,
                        "paramName": output_name}
                }
            }
        elif output_name.startswith("subnetInfra"):
            include_data['paramSubnetInfra' + output_name[-1:]] = {
                "Description": "Public subnet " + output_name[-1:],
                "Type": "AWS::EC2::Subnet::Id",
                "Default": {
                    "StackRef": {
                        "region": {"Ref": "AWS::Region"},
                        "stackName": name,
                        "paramName": output_name}
                }
            }
        elif output_name.startswith("subnetPrivInfra"):
            include_data['paramSubnetPrivInfra' + output_name[-1:]] = {
                "Description": "Private subnet " + output_name[-1:],
                "Type": "AWS::EC2::Subnet::Id",
                "Default": {
                    "StackRef": {
                        "region": {"Ref": "AWS::Region"},
                        "stackName": name,
                        "paramName": output_name}
                }
            }


def setup_networks(name=None, vpc_cidr=None, subnet_prefixlen=None,
                   subnet_base=None, yes=False):
    if name is None and not yes:
        name = raw_input("Infra network name (network): ")
    if not name:
        name = "network"
    default_cidr = Network().vpc_cidr_default()
    if vpc_cidr is None and not yes:
        vpc_cidr = raw_input("VPC CIDR (" + default_cidr + "): ")
    if not vpc_cidr:
        vpc_cidr = default_cidr
    network = ipaddr.IPv4Network(vpc_cidr)
    default_len = network.prefixlen + 4
    if subnet_prefixlen is None and not yes:
        subnet_prefixlen = raw_input("Subnet prefix length (" + str(default_len) + "): ")
    if not subnet_prefixlen:
        subnet_prefixlen = default_len
    default_base = str(network.network)
    if subnet_base is None and not yes:
        subnet_base = raw_input("Subnet base (" + default_base + "): ")
    if not subnet_base:
        subnet_base = default_base
    subnet_base_ip = ipaddr.IPv4Address(subnet_base)
    network_yaml = yaml_load(open(find_include('template-snippets/bootstrap/network.yaml')))
    network_yaml = _get_network_yaml(network, subnet_prefixlen, subnet_base_ip, network_yaml)
    _write_and_deploy_stack(network_yaml, "bootstrap", name, yes)

def _write_and_deploy_stack(network_yaml, component, name, yes):
    stack_dir = os.path.join(".", component, "stack-" + name)
    file_name = "infra-master.properties"
    with open(file_name, 'a'):
        os.utime(file_name, None)
    stack_props = os.path.join(stack_dir, file_name)
    if not os.path.isdir(stack_dir):
        os.makedirs(stack_dir)
    with open(stack_props, 'w') as stack_props_file:
        stack_props_file.write("STACK_NAME=$ORIG_STACK_NAME\n")
    stack_template = os.path.join(stack_dir, "template.yaml")
    with open(stack_template, "w") as stack_file:
        stack_file.write(yaml_save(network_yaml))
    if not yes:
        answer = raw_input("Deploy " + name + " stack? (y): ")
    if yes or answer.lower() == "y" or not answer:
        json_small = json_save_small(network_yaml)
        end_status = cf_deploy.create_or_update_stack(name, json_small, [])
        if end_status == "CREATE_COMPLETE" or end_status == "UPDATE_COMPLETE":
            include_dir = os.path.join(".", "common")
            if not os.path.isdir(include_dir):
                os.makedirs(include_dir)
            network_include_yaml = os.path.join(include_dir, name + ".yaml")
            if os.path.isfile(network_include_yaml):
                with open(network_include_yaml, "r") as network_include_file:
                    include_data = yaml_load(network_include_file)
            else:
                include_data = collections.OrderedDict()
            _get_include_yaml(name, network_yaml, include_data)
            with open(network_include_yaml, "w") as include_file:
                include_file.write(yaml_save(include_data))
        return end_status
    else:
        print yaml_save(network_yaml)
        return "NOT_CREATED"

class ContextClassBase:
    """ Base class for template contexts. Can be directly used for
    bootstrap stacks with no parameters to ask can use it directly
    """
    ask_fields = []
    component_name = "bootstrap"
    stack_name = "Stack name ({0}): "
    branch_mode = BRANCH_MODES.SINGLE_STACK
    template = None

    def __init__(self, ask_fields):
        if not ask_fields:
            ask_fields = ["stack_name"]
        elif not "stack_name" in ask_fields:
            if ask_fields[0] == "component_name":
                ask_fields.insert(1, "stack_name")
            ask_fields.insert(0, "stack_name")
        self.ask_fields = ask_fields

    def stack_name_default(self):
        return "default"

    def set_template(self, template):
        self.template = template

    def format_prompt(self, parameter, default=None):
        prompt = getattr(self, parameter)
        if not default:
            default = getattr(self, parameter + "_default")()
        return prompt.format(default)

    def getattr(self, parameter):
        return getattr(self, parameter)

    def setattr(self, parameter, value):
        return setattr(self, parameter, value)

    def add_context_arguments(self, parser):
        parameters = self.getattr("ask_fields")
        shorts = []
        for param in parameters:
            if not param[0] in shorts:
                shorts.append(param[0])
            else:
                attempt = [x[0] for x in re.split("[\b_]", param)]
                if len(attempt) > 1 and not attempt[1] in shorts:
                    shorts.append(attempt[1])
                else:
                    attempt = param[1]
                    if not attempt in shorts:
                        shorts.append(attempt)
                    else:
                        shorts.append("")
        for short_arg, long_arg in zip(shorts, parameters):
            if short_arg:
                parser.add_argument("-" + short_arg, "--" + long_arg,
                                    help=self.format_prompt(long_arg))
            else:
                parser.add_argument("--" + long_arg, help=self.format_prompt(long_arg))

    def resolve_parameters(self, args):
        for param in self.ask_fields:
            if getattr(args, param):
                setattr(self, param, getattr(args, param))
            elif args.yes:
                setattr(self, param, getattr(args, param + "_default")())
            else:
                default = self.getattr(param + "_default")()
                setval = raw_input(self.format_prompt(param, default=default))
                if not setval:
                    setval = default
                self.setattr(param, setval)

    def write(self, yes=False):
        if "Files" in self.template:
            for next_file in self.template["Files"]:
                for source, dest in next_file:
                    dest = self.component_name + os.sep + dest.replace('${stack}', self.stack_name)
                    if not os.path.exists(os.path.dirname(dest)):
                        os.makedirs(os.path.dirname(dest))
                    source_file = find_include(source)
                    shutil.copy2(source_file, dest)
            self.template.pop("Files", None)
        stack_dir = os.path.join(".", self.component_name, "stack-" + self.stack_name)
        if not os.path.exists(stack_dir):
            os.makedirs(stack_dir)
        if self.branch_mode == BRANCH_MODES.SINGLE_STACK:
            file_name = "infra.properties"
            stack_props = os.path.join(stack_dir, file_name)
            if not os.path.exists(stack_props):
                with open(stack_props, 'w') as stack_props_file:
                    stack_props_file.write("STACK_NAME=$ORIG_STACK_NAME\n")
        stack_template = os.path.join(stack_dir, "template.yaml")
        if os.path.exists(stack_template) and not yes:
            answer = raw_input("Overwrite " + self.stack_name + " stack? (n): ")
            if not answer or not answer.lower() == "y":
                return False
        with open(stack_template, "w") as stack_file:
            stack_file.write(yaml_save(self.template))
        return True

class Network(ContextClassBase):
    stack_name = "Network stack name ({0}): "
    vpc_cidr = "VPC CIDR ({0}) "
    subnet_prefixlen = "Subnet prefix length ({0}) "
    subnet_base = "Subnet base ({0}) "
    last_vpc_cidr = None

    def __init__(self):
        ContextClassBase.__init__(self, ['vpc_cidr', 'subnet_prefixlen', 'subnet_base'])


    def stack_name_default(self):
        return "network"

    def vpc_cidr_default(self):
        self.last_vpc_cidr = "10." + str(random.randint(0, 255)) + ".0.0/16"
        return self.last_vpc_cidr

    def subnet_prefixlen_default(self):
        try:
            nw = ipaddr.IPv4Network(self.vpc_cidr)
            return nw.prefixlen + 4
        except:
            try:
                nw = ipaddr.IPv4Network(self.last_vpc_cidr)
                return nw.prefixlen + 4
            except:
                return 20

    def subnet_base_default(self):
        try:
            nw = ipaddr.IPv4Network(self.vpc_cidr)
            return nw.network
        except:
            try:
                nw = ipaddr.IPv4Network(self.last_vpc_cidr)
                return nw.network
            except:
                return "10." + str(random.randint(0, 255)) + ".0.0"

    def set_template(self, template):
        self.template = _get_network_yaml(self.stack_name, self.subnet_prefixlen,
                                          self.subnet_base, template)

    def write(self, yes=False):
        ContextClassBase.write(self, yes=yes)

class BakeryRoles(ContextClassBase):

    network_stacks = []
    vault_stacks = []
    network_stack = "Network stack ({0}):\n"
    vault_stack = "Vault stack ({0}):\n"
    def __init__(self):
        ContextClassBase.__init__(self, ['network_stack', 'vault_stack'])
        mapper = lambda stack: stack['StackName']
        network_sel = lambda stack: has_output_selector(stack, "VPC", mapper)
        vault_sel = lambda stack: has_output_selector(stack, "decryptPolicy", mapper)
        self.network_stacks = select_stacks(network_sel)
        if self.network_stacks:
            index = 1
            for stack_name in self.network_stacks:
                self.network_stack = self.network_stack + str(index) + ": " + \
                                     stack_name + "\n"
                index = index + 1
        self.vault_stacks = select_stacks(vault_sel)
        if self.vault_stacks:
            index = 1
            for stack_name in self.vault_stacks:
                self.vault_stack = self.vault_stack + str(index) + ": " + \
                                     stack_name + "\n"
                index = index + 1

    def stack_name_default(self):
        return "bakery-roles"

    def network_stack_default(self):
        return "1"

    def vault_stack_default(self):
        return "1"

    def set_template(self, template):
        ContextClassBase.set_template(self, template)
        try:
            index = int(self.network_stack) - 1
            self.template['Parameters']['paramNetworkStack']['Default'] = self.network_stacks[index]
        except (ValueError, IndexError):
            print "Invalid network stack selection " + self.network_stack
            sys.exit(1)
