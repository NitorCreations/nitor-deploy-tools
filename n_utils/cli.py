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
import locale
import os
import sys
import time
from subprocess import PIPE, Popen
import argcomplete
from argcomplete import USING_PYTHON2, ensure_str, split_line
from argcomplete.completers import ChoicesCompleter, FilesCompleter
from pygments import highlight, lexers, formatters
from pygments.styles import get_style_by_name
from . import aws_infra_util
from . import cf_bootstrap
from . import cf_deploy
from . import cf_utils
from . import volumes
from . import COMMAND_MAPPINGS
from .cf_utils import InstanceInfo, is_ec2, region, regions, stacks, \
    stack_params_and_outputs, get_images, promote_image, \
    share_to_another_region, set_region, register_private_dns
from .log_events import CloudWatchLogs, CloudFormationEvents
from .maven_utils import add_server

SYS_ENCODING = locale.getpreferredencoding()

def ndt_register_complete():
    """Print out shell function and command to register ndt command completion
    """
    print """_ndt_complete() {
    local IFS=$'\\013'
    local COMP_CUR="${COMP_WORDS[COMP_CWORD]}"
    local COMP_PREV="${COMP_WORDS[COMP_CWORD-1]}"
    local SUPPRESS_SPACE=0
    if compopt +o nospace 2> /dev/null; then
        SUPPRESS_SPACE=1
    fi
    COMPREPLY=( $(IFS="$IFS" \\
                  COMP_LINE="$COMP_LINE" \\
                  COMP_POINT="$COMP_POINT" \\
                  COMP_TYPE="$COMP_TYPE" \\
                  COMP_CUR="$COMP_CUR" \\
                  COMP_PREV="$COMP_PREV" \\
                  COMP_CWORD=$COMP_CWORD \\
                  _ARGCOMPLETE_COMP_WORDBREAKS="$COMP_WORDBREAKS" \\
                  _ARGCOMPLETE=1 \\
                  _ARGCOMPLETE_SUPPRESS_SPACE=$SUPPRESS_SPACE \\
                  "$1" 8>&1 9>&2 1>/dev/null 2>/dev/null) )
    if [[ $? != 0 ]]; then
        unset COMPREPLY
    elif [[ $SUPPRESS_SPACE == 1 ]] && [[ "$COMPREPLY" =~ [=/:]$ ]]; then
        compopt -o nospace
    fi
}
complete -o nospace -F _ndt_complete "ndt"
"""

def do_command_completion():
    """ ndt command completion function
    """
    output_stream = os.fdopen(8, "wb")
    ifs = os.environ.get("_ARGCOMPLETE_IFS", "\v")
    if len(ifs) != 1:
        sys.exit(1)
    current = os.environ["COMP_CUR"]
    prev = os.environ["COMP_PREV"]
    comp_line = os.environ["COMP_LINE"]
    comp_point = int(os.environ["COMP_POINT"])

    # Adjust comp_point for wide chars
    if USING_PYTHON2:
        comp_point = len(comp_line[:comp_point].decode(SYS_ENCODING))
    else:
        comp_point = len(comp_line.encode(SYS_ENCODING)[:comp_point].decode(SYS_ENCODING))

    comp_line = ensure_str(comp_line)
    comp_words = split_line(comp_line, comp_point)[3]
    if "COMP_CWORD" in os.environ and os.environ["COMP_CWORD"] == "1":
        keys = [x for x in COMMAND_MAPPINGS.keys() if x.startswith(current)]
        output_stream.write(ifs.join(keys).encode(SYS_ENCODING))
        output_stream.flush()
        sys.exit(0)
    else:
        command = prev
        if len(comp_words) > 1:
            command = comp_words[1]
        if not command in COMMAND_MAPPINGS:
            sys.exit(1)
        command_type = COMMAND_MAPPINGS[command]
        if command_type == "shell":
            command = command + ".sh"
        if command_type == "ndtshell":
            command = command + ".sh"
        if command_type == "ndtshell" or command_type == "ndtscript":
            command = aws_infra_util.find_include(command)
        if command_type == "shell" or command_type == "script" or \
           command_type == "ndtshell" or command_type == "ndtscript":
            proc = Popen([command], stderr=PIPE, stdout=PIPE)
            output = proc.communicate()[0]
            if proc.returncode == 0:
                output_stream.write(output.replace("\n", ifs).decode(SYS_ENCODING))
                output_stream.flush()
            else:
                sys.exit(1)
        else:
            line = comp_line[3:].lstrip()
            os.environ['COMP_POINT'] = str(comp_point - (len(comp_line) - \
                                           len(line)))
            os.environ['COMP_LINE'] = line
            parts = command_type.split(":")
            getattr(__import__(parts[0], fromlist=[parts[1]]), parts[1])()
        sys.exit(0)

def ndt():
    """ The main nitor deploy tools command that provides bash command
    completion and subcommand execution
    """
    if "_ARGCOMPLETE" in os.environ:
        do_command_completion()
    else:
        if len(sys.argv) < 2 or sys.argv[1] not in COMMAND_MAPPINGS:
            sys.stderr.writelines([u'usage: ndt <command> [args...]\n'])
            sys.stderr.writelines([u'\tcommand shoud be one of:\n'])
            for command in sorted(COMMAND_MAPPINGS):
                sys.stderr.writelines([u'\t\t' + command + '\n'])
            sys.exit(1)
        command = sys.argv[1]
        command_type = COMMAND_MAPPINGS[command]
        if command_type == "shell":
            command = command + ".sh"
        if command_type == "ndtshell":
            command = command + ".sh"
        if command_type == "ndtshell" or command_type == "ndtscript":
            command = aws_infra_util.find_include(command)
        if command_type == "shell" or command_type == "script" or \
           command_type == "ndtshell" or command_type == "ndtscript":
            sys.exit(Popen([command] + sys.argv[2:]).wait())
        else:
            parts = command_type.split(":")
            my_func = getattr(__import__(parts[0], fromlist=[parts[1]]),
                              parts[1])
            sys.argv = sys.argv[1:]
            sys.argv[0] = "ndt " + sys.argv[0]
            my_func()

def list_file_to_json():
    """ Convert a file with an entry on each line to a json document with
    a single element (name as argument) containg file rows as  list.
    """
    parser = argparse.ArgumentParser(description=list_file_to_json.__doc__)
    parser.add_argument("arrayname", help="The name in the json object given" +\
                                          "to the array").completer = \
                                                            ChoicesCompleter(())
    parser.add_argument("file", help="The file to parse").completer = \
                                                            FilesCompleter()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    content = [line.rstrip('\n') for line in open(args.file)]
    json.dump({args.arrayname : content}, sys.stdout)

def add_deployer_server():
    """Add a server into a maven configuration file. Password is taken from the
    environment variable 'DEPLOYER_PASSWORD'
    """
    parser = argparse.ArgumentParser(description=add_deployer_server.__doc__)
    parser.add_argument("file", help="The file to modify").completer = \
                                                                FilesCompleter()
    parser.add_argument("username",
                        help="The username to access the server.").completer = \
                                                            ChoicesCompleter(())
    parser.add_argument("--id", help="Optional id for the server. Default is" +\
                                     " deploy. One server with this id is " +\
                                     "added and another with '-release' " +\
                                     "appended", default="deploy").completer = \
                                                            ChoicesCompleter(())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    add_server(args.file, args.id, args.username)
    add_server(args.file, args.id + "-release", args.username)

def get_userdata():
    """Get userdata defined for an instance into a file
    """
    parser = argparse.ArgumentParser(description=get_userdata.__doc__)
    parser.add_argument("file", help="File to write userdata into").completer =\
                                                                FilesCompleter()
    argcomplete.autocomplete(parser)
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

def colorprint(data, output_format="yaml"):
    """ Colorized print for either a yaml or a json document given as argument
    """
    lexer = lexers.get_lexer_by_name(output_format)
    formatter = formatters.get_formatter_by_name("256")
    formatter.__init__(style=get_style_by_name('emacs'))
    colored = highlight(unicode(data, 'UTF-8'), lexer, formatter)
    sys.stdout.write(colored.encode(locale.getpreferredencoding()))

def yaml_to_json():
    """"Convert Nitor CloudFormation yaml to CloudFormation json with some
    preprosessing
    """
    parser = argparse.ArgumentParser(description=yaml_to_json.__doc__)
    parser.add_argument("--colorize", "-c", help="Colorize output",
                        action="store_true")
    parser.add_argument("file", help="File to parse").completer = FilesCompleter()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    doc = aws_infra_util.yaml_to_json(args.file)
    if args.colorize:
        colorprint(doc)
    else:
        print doc

def json_to_yaml():
    """Convert CloudFormation json to an approximation of a Nitor CloudFormation
    yaml with for example scripts externalized
    """
    parser = argparse.ArgumentParser(description=json_to_yaml.__doc__)
    parser.add_argument("--colorize", "-c", help="Colorize output",
                        action="store_true")
    parser.add_argument("file", help="File to parse").completer = FilesCompleter()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    doc = aws_infra_util.json_to_yaml(args.file)
    if args.colorize:
        colorprint(doc)
    else:
        print doc

def read_and_follow():
    """Read and print a file and keep following the end for new data
    """
    parser = argparse.ArgumentParser(description=read_and_follow.__doc__)
    parser.add_argument("file", help="File to follow").completer = FilesCompleter()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    cf_utils.read_and_follow(args.file, sys.stdout.write)

def logs_to_cloudwatch():
    """Read a file and send rows to cloudwatch and keep following the end for
    new data
    """
    parser = argparse.ArgumentParser(description=logs_to_cloudwatch.__doc__)
    parser.add_argument("file", help="File to follow").completer = FilesCompleter()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if not os.path.isfile(args.file):
        parser.error(args.file + " not found")
    cf_utils.send_logs_to_cloudwatch(args.file)

def signal_cf_status():
    """Signal CloudFormation status to a logical resource in CloudFormation
    that is either given on the command line or resolved from CloudFormation
    tags
    """
    parser = argparse.ArgumentParser(description=signal_cf_status.__doc__)
    parser.add_argument("status",
                        help="Status to indicate: SUCCESS | FAILURE").completer\
                                      = ChoicesCompleter(("SUCCESS", "FAILURE"))
    parser.add_argument("-r", "--resource", help="Logical resource name to " +\
                                                 "signal. Looked up from " +\
                                                 "cloudformation tags by " +\
                                                 "default")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.status != "SUCCESS" and args.status != "FAILURE":
        parser.error("Status needs to be SUCCESS or FAILURE")
    cf_utils.signal_status(args.status, resource_name=args.resource)

def associate_eip():
    """Associate an Elastic IP for the instance
    """
    parser = argparse.ArgumentParser(description=associate_eip.__doc__)
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
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    cf_utils.associate_eip(eip=args.ip, allocation_id=args.allocationid,
                           eip_param=args.eipparam,
                           allocation_id_param=args.allocationidparam)

def instance_id():
    """ Get id for instance
    """
    parser = argparse.ArgumentParser(description=instance_id.__doc__)
    argcomplete.autocomplete(parser)
    if is_ec2():
        info = InstanceInfo()
        print info.instance_id()
    else:
        sys.exit(1)

def ec2_region():
    """ Get default region - the region of the instance if run in an EC2 instance
    """
    parser = argparse.ArgumentParser(description=region.__doc__)
    argcomplete.autocomplete(parser)
    print region()

def tag():
    """ Get the value of a tag for an ec2 instance
    """
    parser = argparse.ArgumentParser(description=tag.__doc__)
    parser.add_argument("name", help="The name of the tag to get")
    args = parser.parse_args()
    argcomplete.autocomplete(parser)
    if is_ec2():
        info = InstanceInfo()
        value = info.tag(args.name)
        if value is not None:
            print value
        else:
            sys.exit("Tag " + args.name + "not found")
    else:
        parser.error("Only makes sense on an EC2 instance")

def stack_name():
    """ Get name of the stack that created this instance
    """
    parser = argparse.ArgumentParser(description=stack_name.__doc__)
    argcomplete.autocomplete(parser)
    if is_ec2():
        info = InstanceInfo()
        print info.stack_name()
    else:
        parser.error("Only makes sense on an EC2 instance cretated from a CF stack")

def stack_id():
    """ Get id of the stack the creted this instance
    """
    parser = argparse.ArgumentParser(description=stack_id.__doc__)
    argcomplete.autocomplete(parser)
    if is_ec2():
        info = InstanceInfo()
        print info.stack_id()
    else:
        parser.error("Only makes sense on an EC2 instance cretated from a CF stack")

def logical_id():
    """ Get the logical id that is expecting a signal from this instance
    """
    parser = argparse.ArgumentParser(description=logical_id.__doc__)
    argcomplete.autocomplete(parser)
    if is_ec2():
        info = InstanceInfo()
        print info.logical_id()
    else:
        parser.error("Only makes sense on an EC2 instance cretated from a CF stack")

def cf_region():
    """ Get region of the stack that created this instance
    """
    parser = argparse.ArgumentParser(description=cf_region.__doc__)
    argcomplete.autocomplete(parser)
    if is_ec2():
        info = InstanceInfo()
        print info.stack_id().split(":")[3]
    else:
        parser.error("Only makes sense on an EC2 instance cretated from a CF stack")

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
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help="Do not actually deploy anything, but just " +\
                             "assemble the json and associated parameters")
    args = parser.parse_args()
    if not os.path.isfile(args.yaml_template):
        parser.error(args.yaml_template + " not found")
    cf_deploy.deploy(args.stack_name, args.yaml_template, args.region,
                     args.dry_run)
    return

def delete_stack():
    """Create or update existing CloudFormation stack
    """
    parser = argparse.ArgumentParser(description=delete_stack.__doc__)
    parser.add_argument("stack_name", help="Name of the stack to delete")
    parser.add_argument("region", help="The region to delete the stack from")
    args = parser.parse_args()
    cf_deploy.delete(args.stack_name, args.region)
    return

def tail_stack_logs():
    """Tail logs from the log group of a cloudformation stack
    """
    parser = argparse.ArgumentParser(description=tail_stack_logs.__doc__)
    parser.add_argument("stack_name", help="Name of the stack to watch logs " +\
                                           "for")
    parser.add_argument("-s", "--start", help="Start time in seconds since" +\
                                              "epoc")
    argcomplete.autocomplete(parser)
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
    parser = argparse.ArgumentParser(description=resolve_include.__doc__)
    parser.add_argument("file", help="The file to find")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    inc_file = aws_infra_util.find_include(args.file)
    if not inc_file:
        parser.error("Include " + args.file + " not found on include paths " +\
                     str(aws_infra_util.include_dirs))
    print inc_file

def assume_role():
    """Assume a defined role. Prints out environment variables
    to be eval'd to current context for use:
    eval $(assume-role 'arn:aws:iam::43243246645:role/DeployRole')
    """
    parser = argparse.ArgumentParser(description=assume_role.__doc__)
    parser.add_argument("role_arn", help="The ARN of the role to assume")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    creds = cf_utils.assume_role(args.role_arn)
    print "AWS_ACCESS_KEY_ID=\"" + creds['AccessKeyId'] + "\""
    print "AWS_SECRET_ACCESS_KEY=\"" + creds['SecretAccessKey'] + "\""
    print "AWS_SESSION_TOKEN=\"" + creds['SessionToken'] + "\""
    print "export AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN"

def get_parameter():
    """Get a parameter value from the stack
    """
    parser = argparse.ArgumentParser(description=get_parameter.__doc__)
    parser.add_argument("parameter", help="The name of the parameter to print")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    info = InstanceInfo()
    print info.stack_data(args.parameter)

def volume_from_snapshot():
    """ Create a volume from an existing snapshot and mount it on the given
    path. The snapshot is identified by a tag key and value. If no tag is
    found, an empty volume is created, attached, formatted and mounted.
    """
    parser = argparse.ArgumentParser(description=volume_from_snapshot.__doc__)
    parser.add_argument("tag_key", help="Key of the tag to find volume with")
    parser.add_argument("tag_value", help="Value of the tag to find volume with")
    parser.add_argument("mount_path", help="Where to mount the volume")
    parser.add_argument("size_gb", nargs="?", help="Size in GB for the volum" +\
                                                   "e. If different from sna" +\
                                                   "pshot size, volume and " +\
                                                   "filesystem are resized",
                        default=None, type=int)
    argcomplete.autocomplete(parser)
    if is_ec2():
        args = parser.parse_args()
        volumes.volume_from_snapshot(args.tag_key, args.tag_value, args.mount_path,
                                     size_gb=args.size_gb)
    else:
        parser.error("Only makes sense on an EC2 instance")

def snapshot_from_volume():
    """ Create a snapshot of a volume identified by it's mount path
    """
    parser = argparse.ArgumentParser(description=snapshot_from_volume.__doc__)
    parser.add_argument("tag_key", help="Key of the tag to find volume with")
    parser.add_argument("tag_value", help="Value of the tag to find volume with")
    parser.add_argument("mount_path", help="Where to mount the volume")
    argcomplete.autocomplete(parser)
    if is_ec2():
        args = parser.parse_args()
        volumes.create_snapshot(args.tag_key, args.tag_value, args.mount_path)
    else:
        parser.error("Only makes sense on an EC2 instance")

def detach_volume():
    """ Create a snapshot of a volume identified by it's mount path
    """
    parser = argparse.ArgumentParser(description=snapshot_from_volume.__doc__)
    parser.add_argument("mount_path", help="Where to mount the volume")
    argcomplete.autocomplete(parser)
    if is_ec2():
        args = parser.parse_args()
        volumes.detach_volume(args.mount_path)
    else:
        parser.error("Only makes sense on an EC2 instance")


def clean_snapshots():
    """Clean snapshots that are older than a number of days (30 by default) and
    have one of specified tag values
    """
    parser = argparse.ArgumentParser(description=clean_snapshots.__doc__)
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
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if args.region:
        os.environ['AWS_DEFAULT_REGION'] = args.region
    volumes.clean_snapshots(args.days, args.tags)

def setup_cli():
    """Setup the command line environment to define an aws cli profile with
    the given name and credentials. If an identically named profile exists,
    it will not be overwritten.
    """
    parser = argparse.ArgumentParser(description=setup_cli.__doc__)
    parser.add_argument("-n", "--name", help="Name for the profile to create")
    parser.add_argument("-k", "--key-id", help="Key id for the profile")
    parser.add_argument("-s", "--secret", help="Secret to set for the profile")
    parser.add_argument("-r", "--region", help="Default region for the profile")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    cf_bootstrap.setup_cli(**vars(args))

def setup_networks():
    """Setup a VPC and a private and public network in each availability zone.
    """
    parser = argparse.ArgumentParser(description=setup_networks.__doc__)
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
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    print cf_bootstrap.setup_networks(**vars(args))

def show_stack_params_and_outputs():
    """ Show stack parameters and outputs as a single json documents
    """
    parser = argparse.ArgumentParser(description=show_stack_params_and_outputs.__doc__)
    parser.add_argument("-r", "--region", help="Region for the stack to show",
                        default=region()).completer = ChoicesCompleter(regions())
    parser.add_argument("stack_name", help="The stack name to show").completer = \
        ChoicesCompleter(stacks())
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    resp = stack_params_and_outputs(args.region, args.stack_name)
    print json.dumps(resp, indent=2)

def cli_get_images():
    """ Gets a list of images given a bake job name
    """
    parser = argparse.ArgumentParser(description=cli_get_images.__doc__)
    parser.add_argument("job_name", help="The job name to look for")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    set_region()
    images = get_images(args.job_name)
    for image in images:
        print image['ImageId'] + ":" + image['Name']

def cli_promote_image():
    """  Promotes an image for use in another branch
    """
    parser = argparse.ArgumentParser(description=cli_promote_image.__doc__)
    parser.add_argument("image_id", help="The image to promote")
    parser.add_argument("target_job", help="The job name to promote the image to")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    if ":" in args.image_id:
        args.image_id = args.image_id.split(":")[0]
    promote_image(args.image_id, args.target_job)

def cli_share_to_another_region():
    """ Shares an image to another region for potentially another account
    """
    parser = argparse.ArgumentParser(description=cli_share_to_another_region.__doc__)
    parser.add_argument("ami_id", help="The ami to share")
    parser.add_argument("to_region", help="The region to share to").completer =\
        ChoicesCompleter(regions())
    parser.add_argument("ami_name", help="The name for the ami")
    parser.add_argument("account_id", nargs="+", help="The account ids to sh" +\
                                                      "are ami to")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    share_to_another_region(args.ami_id, args.to_region, args.ami_name,
                            args.account_id)

def cli_register_private_dns():
    """ Register local private IP in route53 hosted zone usually for internal
    use.
    """
    parser = argparse.ArgumentParser(description=cli_register_private_dns.__doc__)
    parser.add_argument("dns_name", help="The name to update in route 53")
    parser.add_argument("hosted_zone", help="The name of the hosted zone to update")
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    register_private_dns(args.dns_name, args.hosted_zone)
