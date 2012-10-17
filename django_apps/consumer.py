#!/usr/bin/env python

import sys
from time import sleep
from cPickle import load

counter=1
try:
    while True:
        i = load(sys.stdin)
        #print >> sys.stderr, "consumer: received", i
		
		
except EOFError:
    pass

#print >> sys.stderr, "objects received", counter
