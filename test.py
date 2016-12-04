#!/usr/bin/env python
from vault import Vault
import sys

vlt = Vault()
enc = vlt.store(sys.argv[1], sys.argv[2].encode())
print str(vlt.lookup(sys.argv[1]))
vlt.delete(sys.argv[1])
