#!/usr/bin/env python
import os, logging
from django_apps.tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_apps.lhcbPR.models import AddedResults
import pushZip

#set custom path for the proxy
#os.environ['X509_USER_PROXY'] = '/afs/cern.ch/user/l/lhcbpr/private/myProxyFile'

#get the logger from the django settings
logger = logging.getLogger('check_logger')

diracStorageElementName = 'StatSE'
#uploaded/ <--- this will be the official one
diracStorageElementFolder = 'uploaded'

addedDiracStorageFolder = 'added'

temp_save_path = os.path.join(settings.PROJECT_PATH, 'static/temp_zipfiles')
local_zip_path = os.path.join(settings.PROJECT_PATH, 'static/zipfiles')


def pushNewResultsLocal():
    for file in os.listdir(local_zip_path):
        if file.endswith(".zip"):
            logger.info('New zip: {0}, found in results directory, calling pushZip command...'.format(file))
            pushZip.pushThis(file)


def pushNewResults():
    #cd to temp folder to temporary save the zip files
    os.chdir(temp_save_path) 
    
    logger.warning('Checking results directory for new added zip files...')

    from DIRAC.Core.Base.Script import initialize
    #from DIRAC import gLogger
    #gLogger.setLevel("DEBUG")
    initialize(ignoreErrors = True, enableCommandLine = False)
    
    from DIRAC.Resources.Storage.StorageElement import StorageElement    
    statSE = StorageElement(diracStorageElementName)
    #print diracStorageElementFolder
    
    print "Before listDirectory"
    dirDict = statSE.listDirectory(diracStorageElementFolder)
    print "After listDirectory"
    print dirDict   
 
    for zipResult in dirDict['Value']['Successful'][diracStorageElementFolder]['Files']:
        fileName, fileExtension = os.path.splitext(zipResult)
        
        #get the File, copy the file to the current local directory
        res = statSE.getFile(os.path.join(diracStorageElementFolder, zipResult))
        if not res['OK'] or ( res['OK'] and len(res['Value']['Failed']) > 0):
            logger.errot("Failed download of " + zipResult)
            continue
        
        results_list = AddedResults.objects.filter(identifier__exact=fileName)

        res = True
        if not results_list:
            logger.info('New zip: {0}, found in results directory, calling pushZip command...'.format(zipResult))
            res = pushZip.pushThis(os.path.join(temp_save_path, zipResult ))
            
        if not res:
            logger.error("Error pushing results, not removing")
            continue

        #remove it from the upload_test folder
        statSE.removeFile(os.path.join(diracStorageElementFolder, zipResult))
        #put the file into the added folder
        statSE.putFile({ os.path.join(addedDiracStorageFolder, zipResult) : zipResult})
        #also remove the file from the current directory
        os.remove(os.path.join(temp_save_path, zipResult))

class Command(BaseCommand):

    def handle(self, *args, **options):
        pushNewResultsLocal()
