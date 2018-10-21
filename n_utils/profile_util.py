from __future__ import print_function
import os
import argparse
import argcomplete
import re
import time
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc
from collections import OrderedDict
from os.path import expanduser, join, exists
from argcomplete.completers import ChoicesCompleter
from ConfigParser import ConfigParser

def read_expiring_profiles():
    ret = []
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        parser = ConfigParser()
        with open(credentials) as credfile:
            parser.readfp(credfile)
            for profile in parser.sections():
                if parser.has_option(profile, "aws_session_expiration"):
                    ret.append(profile)
    return ret

def get_profile(profile):
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        parser = ConfigParser()
        with open(credentials) as credfile:
            parser.readfp(credfile)
            ret = OrderedDict()
            if profile in parser.sections():
                for option in parser.options(profile):
                    ret[option] = parser.get(profile, option)
                return ret
    return {}

def read_profile_expiry(profile):
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        parser = ConfigParser()
        with open(credentials) as credfile:
            parser.readfp(credfile)
            for profile in parser.sections():
                if parser.has_option(profile, "aws_session_expiration"):
                    return parser.get(profile, "aws_session_expiration")
    return ""

def profile_to_env():
    """ Prints profile parameters from credentials file (~/.aws/credentials) as eval-able environment variables """
    parser = argparse.ArgumentParser(description=profile_to_env.__doc__)
    parser.add_argument("-t", "--target-role", action="store_true", help="Output also azure_default_role_arn")
    parser.add_argument("-r", "--role-arn", help="Output also the role given here as the target role for the profile")
    if "_ARGCOMPLETE" in os.environ:
        parser.add_argument("profile", help="The profile to read expiry info from").completer = \
            ChoicesCompleter(read_expiring_profiles())
        argcomplete.autocomplete(parser)
    else:
        parser.add_argument("profile", help="The profile to read expiry info from")
    args = parser.parse_args()
    safe_profile = re.sub("[^A-Z0-9]", "_", args.profile.upper())
    params = []
    role_param = "AWS_TARGET_ROLE_ARN_" + safe_profile
    if args.target_role:
        profile_entry = "profile " + args.profile
        home = expanduser("~")
        config = join(home, ".aws", "config")
        if exists(config):
            parser = ConfigParser()
            with open(config) as configfile:
                parser.readfp(configfile)
                if profile_entry in parser.sections() and parser.has_option(profile_entry, "azure_default_role_arn"):
                    params.append(role_param)
                    print(role_param + "=\"" + parser.get(profile_entry, "azure_default_role_arn") + "\"")
    if args.role_arn:
        params.append(role_param)
        print(role_param + "=\"" + args.role_arn + "\"")
    print_profile(args.profile, params)

def print_profile(profile_name, params):
    safe_profile = re.sub("[^A-Z0-9]", "_", profile_name.upper())
    profile = get_profile(profile_name)
    for key, value in profile.items():
        upper_param = key.upper()
        if key == "aws_session_expiration":
            d = parse(value)
            epoc = int((d - datetime.utcfromtimestamp(0).replace(tzinfo=tzutc())).total_seconds())
            print("AWS_SESSION_EXPIRATION_EPOC_" + safe_profile + "=\"" + str(epoc) + "\"")
            params.append("AWS_SESSION_EXPIRATION_EPOC_" + safe_profile)
        params.append(upper_param)
        if value.startswith("\""):
            value = value[1:-1]
        print(upper_param + "=\"" + value + "\"")
    print("export " + " ".join(params))

def cli_read_profile_expiry():
    """ Read expiry field from credentials file, which is there if the login happened
    with aws-azure-login or another tool that implements the same logic (none currently known)."""
    parser = argparse.ArgumentParser(description=cli_read_profile_expiry.__doc__)
    parser.add_argument("profile", help="The profile to read expiry info from").completer = \
        ChoicesCompleter(read_expiring_profiles())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    print(read_profile_expiry(args.profile))

def update_profile(profile, creds):
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        parser = ConfigParser()
        with open(credentials, 'rb') as credfile:
            parser.readfp(credfile)
            if profile not in parser.sections():
                parser.add_section(profile)
            parser.set(profile, "aws_access_key_id", creds['AccessKeyId'])
            parser.set(profile, "aws_secret_access_key", creds['SecretAccessKey'])
            parser.set(profile, "aws_session_token", creds['SessionToken'])
            parser.set(profile, "aws_session_expiration", creds['Expiration'].strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
    with open(credentials, 'wb') as credfile:
        parser.write(credfile)