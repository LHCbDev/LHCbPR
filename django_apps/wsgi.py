import os, sys
sys.path.append('/afs/cern.ch/user/e/ekiagias/workspace/LHCbPR/')
sys.path.append('/afs/cern.ch/user/e/ekiagias/workspace/LHCbPR/django_apps/')
#sys.path.append("/home/LHCbPR/")
#sys.path.append("/home/LHCbPR/django_apps/")
os.environ['DJANGO_SETTINGS_MODULE'] = 'django_apps.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
