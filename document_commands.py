#!/usr/bin/env python

from n_utils import COMMAND_MAPPINGS, PATH_COMMANDS
from subprocess import Popen, PIPE

def do_call(command):
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = proc.communicate()
    return (output + err).strip().replace("'", "\\'")

for command, c_type in COMMAND_MAPPINGS.iteritems():
    print "### `ndt " + command + "`"
    print ""
    print "```bash"
    print do_call(["ndt", command, "-h"])
    print "```\n"

for script in PATH_COMMANDS:
    name = script.split("/")[-1]
    print "### `" + name + "`"
    print ""
    print "```bash"
    print do_call([name, "-h"])
    print "```\n"
