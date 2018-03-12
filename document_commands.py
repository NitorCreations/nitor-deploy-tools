#!/usr/bin/env python

from n_utils import COMMAND_MAPPINGS
from subprocess import Popen, PIPE

def do_call(command):
    proc = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = proc.communicate()
    return (output + err).strip()

for command, c_type in COMMAND_MAPPINGS.iteritems():
    if c_type == "script":
        print "### `" + command + "`"
        print ""
        print "```bash"
        print do_call([command, "-h"])
    else:
        print "### `ndt " + command + "`"
        print ""
        print "```bash"
        print do_call(["ndt", command, "-h"])
    print "```\n"
