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
