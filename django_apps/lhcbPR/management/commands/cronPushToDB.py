#!/usr/bin/env python
import os, logging
from tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lhcbPR.models import AddedResults
import pushZip

os.environ['X509_USER_PROXY'] = '/afs/cern.ch/user/l/lhcbpr/private/myProxyFile'

#get the logger from the django settings
logger = logging.getLogger('check_logger')

diracStorageElementName = 'StatSE'
#uploaded/ <--- this will be the official one
diracStorageElementFolder = 'uploaded_test'
addedDiracStorageFolder = 'added'

temp_save_path = os.path.join(settings.PROJECT_PATH, 'static/images/histograms')

def pushNewResults():
    #cd to temp folder to temporary save the zip files
    #before save in the database, for the testing are saved static/images/histograms
    #where the vm alamages has permissions to write
    os.chdir(temp_save_path) 
    
    logger.info('Checking results directory for new added zip files...')
    
    from DIRAC.Core.Base.Script import parseCommandLine, initialize
    initialize(ignoreErrors = True, enableCommandLine = False)
    
    from DIRAC.Resources.Storage.StorageElement import StorageElement    
    statSE = StorageElement(diracStorageElementName)
    
    dirDict = statSE.listDirectory(diracStorageElementFolder)
    
    for zipResult in dirDict['Value']['Successful'][diracStorageElementFolder]['Files']:
        fileName, fileExtension = os.path.splitext(zipResult)
        
        #get the File
        statSE.getFile(os.path.join(diracStorageElementFolder, zipResult))
        
        results_list = AddedResults.objects.filter(identifier__exact=fileName)
        if not results_list:
            logger.info('New zip: {0}, founded in results directory, calling pushZip command...'.format(zipResult))
            pushZip.pushThis('{0}{1}{2}'.format(temp_save_path, os.sep, zipResult))
        
        #remove it from the upload_test folder
        statSE.removeFile(os.path.join(diracStorageElementFolder, zipResult))
        #put the file into the added folder
        statSE.putFile({ os.path.join(addedDiracStorageFolder, zipResult) : zipResult})
        #also remove the file from the current directory
        os.remove(zipResult)

class Command(BaseCommand):

    def handle(self, *args, **options):
    
        if len(args) == 1 and args[0] == 'pythoncron':
            c = CronTab(
              Event( pushNewResults, min = range(0,60,5) )
            )
            c.run()
        else:
            pushNewResults()
