import os, sys, inspect

work_path = os.path.dirname(inspect.getfile(inspect.currentframe()))
parent_work_path = os.path.dirname(work_path)

sys.path.append(parent_work_path)
sys.path.append(work_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'django_apps.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
