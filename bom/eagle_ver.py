#!/bin/env python
import sys

if len(sys.argv) != 2:
    print "Usage: eagle_ver.py SCH_FILE"
    sys.exit(1)

f = open( sys.argv[1], "r" )

f.seek( 8 )
b = f.read(2)

print "%i.%i" % (ord(b[0]), ord(b[1]))

