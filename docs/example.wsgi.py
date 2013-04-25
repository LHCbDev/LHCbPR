import os, sys, inspect

#this is a wsgi example file to deploy django with wsgi 

#let's assume that the wsgi file exists in the LHCbPR/django_apps/
#so we append to the system the work_path which is LHCbPR/django_apps
#and the parent path LHCbPR
work_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
parent_work_path = os.path.dirname(work_path)

sys.path.append(parent_work_path)
sys.path.append(work_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_apps.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
