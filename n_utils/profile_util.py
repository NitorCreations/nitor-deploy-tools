from __future__ import print_function
import os
import argparse
import argcomplete
import re
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc
from os.path import expanduser, join, exists
from argcomplete.completers import ChoicesCompleter
from iniconfig import IniConfig

def read_expiring_profiles():
    ret = []
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        ini = IniConfig(credentials)
        for profile in ini.sections.keys():
            if "aws_session_expiration" in ini[profile]:
                ret.append(profile)
    return ret

def get_profile(profile):
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        ini = IniConfig(credentials)
        if profile in ini:
            return ini[profile]
    return {}

def read_profile_expiry(profile):
    home = expanduser("~")
    credentials = join(home, ".aws", "credentials")
    if exists(credentials):
        ini = IniConfig(credentials)
        if profile in ini.sections:
            if "aws_session_expiration" in ini[profile]:
                return ini[profile]["aws_session_expiration"]
    return ""

def profile_to_env():
    """ Prints profile parameters from credentials file (~/.aws/credentials) as eval-able environment variables """
    parser = argparse.ArgumentParser(description=profile_to_env.__doc__)
    if "_ARGCOMPLETE" in os.environ:
        parser.add_argument("profile", help="The profile to read expiry info from").completer = \
            ChoicesCompleter(read_expiring_profiles())
        argcomplete.autocomplete(parser)
    else:
        parser.add_argument("profile", help="The profile to read expiry info from")
    parser.add_argument("-t", "--target-role", action="store_true", help="Output also azure_default_role_arn")
    args = parser.parse_args()
    params = []
    safe_profile = re.sub("[^A-Z0-9]", "_", args.profile.upper())
    if args.target_role:
        role_param = "AWS_TARGET_ROLE_ARN_" + safe_profile
        profile_entry = "profile " + args.profile
        home = expanduser("~")
        config = join(home, ".aws", "config")
        ini = IniConfig(config)
        if profile_entry in ini and "azure_default_role_arn" in ini[profile_entry]:
            params.append(role_param)
            print(role_param + "=\"" + ini[profile_entry]["azure_default_role_arn"] + "\"")
    profile = get_profile(args.profile)
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
