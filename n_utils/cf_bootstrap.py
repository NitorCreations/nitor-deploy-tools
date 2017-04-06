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
import stat
from copy import deepcopy

import boto3
import ipaddr
from . import cf_deploy
from awscli.customizations.configure.writer import ConfigFileWriter
from .aws_infra_util import find_include, yaml_load, json_save_small, yaml_save

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
        resources.update({route_table[:-1] + letter: route_table_dict })
    route_table_assoc_dict = deepcopy(resources[route_table_assoc])
    if not public:
        route_table_assoc_dict['Properties']['RouteTableId']['Ref'] = \
            route_table[:-1] + letter
    route_table_assoc_dict['Properties']['SubnetId']['Ref'] = \
        subnet_to_create
    resources.update({route_table_assoc[:-1] + letter: route_table_assoc_dict})

    resources[db_subnet]['Properties']['SubnetIds'].append({"Ref": subnet_to_create})

def _get_network_yaml(network, subnet_prefixlen, subnet_base):
    subnet_bits = 32 - subnet_prefixlen
    subnet_size = 2 ** subnet_bits
    ec2 = boto3.client("ec2")
    az_response = ec2.describe_availability_zones()
    last_subnet = subnet_base  - subnet_size
    az_names = sorted([az_data['ZoneName'] for az_data in \
               az_response['AvailabilityZones']])
    network_yaml = yaml_load(open(find_include('template-snippets/vpc.yaml')))
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
                "Value": { "Ref": "resourcePubSubnet" + zone_upper_letter },
                "Export": { "Name": { "Fn::Join": [":", [{"Ref": "AWS::StackName"}, "publicSubnet" + zone_upper_letter]] } }
            }
            network_yaml['Outputs']['subnetPrivInfra' + zone_upper_letter] = {
                "Description": "Private Subnet " + zone_upper_letter,
                "Value": { "Ref": "resourcePrivSubnet" + zone_upper_letter },
                "Export": { "Name": { "Fn::Join": [":", [{"Ref": "AWS::StackName"}, "privateSubnet" + zone_upper_letter]] } }
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
    default_cidr = "10." + str(random.randint(0, 255)) + ".0.0/16"
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
    subnet_base = ipaddr.IPv4Address(subnet_base)
    network_yaml = _get_network_yaml(network, subnet_prefixlen, subnet_base)
    stack_dir = os.path.join(".", "bootstrap", "stack-" + name)
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
        answer = raw_input("Deploy network stack? (y): ")
    if yes or answer.lower() == "y" or not answer:
        json_small = json_save_small(network_yaml)
        end_status = cf_deploy.create_or_update_stack(name, json_small, [])
        if end_status == "CREATE_COMPLETE" or end_status == "UPDATE_COMPLETE":
            include_dir = os.path.join(".", "common")
            if not os.path.isdir(include_dir):
                os.makedirs(include_dir)
            network_include_yaml = os.path.join(include_dir, "network.yaml")
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
