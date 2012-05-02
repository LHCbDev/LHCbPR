import os, sys
#import configs
sys.path.append('/afs/cern.ch/user/e/ekiagias/workspace/database_test/')
sys.path.append('/afs/cern.ch/user/e/ekiagias/workspace/database_test/database_test/')
#sys.path.append("/home/database_test/")
#sys.path.append("/home/database_test/database_test/")
os.environ['DJANGO_SETTINGS_MODULE'] = 'database_test.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
