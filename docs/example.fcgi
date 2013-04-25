#!/usr/bin/python2.6

#this is an example fcgi file to deploy django project with fcgi module
#this is the fcgi currently used cern.ch/lhcb-pr production release

import sys, os

# Add a custom Python path.
root="/afs/cern.ch/lhcb/software/webapps/LHCbPR"
#sys.path.insert(0, "%s/Django-1.4.3" %root)
sys.path.insert(0, "%s/Django-1.3.5" %root)
sys.path.insert(0, "%s/flup-1.0.2" %root)
sys.path.insert(0, "%s/LHCbPR" %root)
sys.path.insert(0, "%s/LHCbPR/django_apps" %root)


#just some more comments

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
