# Django settings for database_test project.

import os, socket
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Emmanouil Kiagias', 'emmanouil.kiagias@cern.ch'),
)

#try to get the hostname(machine)
try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

MANAGERS = ADMINS

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.oracle', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
    #    'NAME': 'devdb11',                      # Or path to database file if using sqlite3.
    #    'USER': 'LHCB_PR',                      # Not used with sqlite3.
    #    'PASSWORD': 'Xe_masi31',                  # Not used with sqlite3.
    #    'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
    #    'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    #}
    #database for lhcbpr virtual machine
    'default': {
        'ENGINE': 'django.db.backends.oracle', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'devdb11',                      # Or path to database file if using sqlite3.
        'USER': 'lhcb_prtest',                      # Not used with sqlite3.
        'PASSWORD': 'Lekuwu49',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }

}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Zurich'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static/files/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/files/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/no_static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)
LOGIN_REDIRECT_URL = '/django/lhcbPR'
SHIB_SSO_ADMIN = True
SHIB_SSO_CREATE_ACTIVE = True
SHIB_SSO_CREATE_STAFF = False
SHIB_SSO_CREATE_SUPERUSER = False
SHIB_LOGIN_PATH = '/Shibboleth.sso/?target='
SHIB_LOGOUT_URL = 'https://login.cern.ch/adfs/ls/?wa=wsignout1.0&returnurl='
META_EMAIL = 'ADFS_EMAIL'
META_FIRSTNAME = 'ADFS_FIRSTNAME'
META_GROUP = 'ADFS_GROUP'
META_LASTNAME = 'ADFS_LASTNAME'
META_USERNAME = 'ADFS_LOGIN'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@-h+b4bed6jk&9ef5ky^q98chxg!*sbn5evtpr8n1fnxh&d@=3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'shibsso.middleware.ShibSSOMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

AUTHENTICATION_BACKENDS = (
        'shibsso.backends.ShibSSOBackend',
)

ROOT_URLCONF = 'django_apps.urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates')
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'shibsso',
    'lhcbPR',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


#soon to be moved from here
HISTOGRAMSGAUSS = {
              'Num. of primary interaction per bunch' : 'GenMonitorAlg/10',
              'PrimaryVertex y (mm)' :  'GenMonitorAlg/12',
              'Multiplicity stable charged particles in LHCb eta' : 'GenMonitorAlg/4',
              'PrimaryVertex x (mm)' : 'GenMonitorAlg/11',
              'PrimaryVertex z (mm)' :  'GenMonitorAlg/13',
              'Pseudorapidity stable charged particles' : 'GenMonitorAlg/44',
              'Multiplicity stable charged particles' : 'GenMonitorAlg/3',
              'Pt stable charged particles' : 'GenMonitorAlg/45',
              'Process type' : 'GenMonitorAlg/5',
}
HISTOGRAMSGAUSSOPTIONS = {
              'GenMonitorAlg/10' : [ 'Nint', '1/Nev', False, False, 'hist' ],
              'GenMonitorAlg/12': [ 'y (mm)', 'Nvert/Nev', False, False, 'hist'],
              'GenMonitorAlg/4' :[ 'Npart', 'dN', False, True, 'hist' ],
              'GenMonitorAlg/11': [ 'x (mm)' ,'Nvert/Nev', False, False, 'hist' ],
              'GenMonitorAlg/13': [ 'z (mm)', 'Nvert/Nev', False, False, 'hist' ],
              'GenMonitorAlg/44': [ 'eta', 'dN/eta', False, False, 'hist' ],
              'GenMonitorAlg/3': [ 'Npart', 'dN', False, True, 'hist' ],
              'GenMonitorAlg/45': [  'Pt (MeV)', 'dN/pt', False, True, 'hist' ],
              'GenMonitorAlg/5': [  'Process id', '', False, False, 'hist' ],
}