#!/usr/bin/env python
import os, logging
from tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lhcbPR.models import AddedResults
import pushZip

#directories for results logging
log_file_path = os.path.join(settings.PROJECT_PATH, 'static/logs/adding_results_log')
results_directory = os.path.join(settings.PROJECT_PATH, 'static/uploaded')

logger = logging.getLogger('cronPushToDB')
filehandler = logging.FileHandler(log_file_path)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler) 
logger.setLevel(logging.INFO)

diracStorageElementName = 'StatSE'
#uploaded/ <--- this will be the official one
diracStorageElementFolder = 'uploaded_test'
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
        
        statSE.getFile('{0}{1}{2}'.format(diracStorageElementFolder, os.sep, zipResult))
    
        results_list = AddedResults.objects.filter(identifier__exact=fileName)
        if not results_list:
            logger.info('New zip: {0}, founded in results directory, calling pushZip command...'.format(zipResult))
            pushZip.pushThis('{0}{1}{2}'.format(temp_save_path, os.sep, zipResult))
        os.remove(zipResult)

class Command(BaseCommand):

    def handle(self, *args, **options):
    
        c = CronTab(
          Event( pushNewResults, min = range(0,60,1) )
        )
        c.run()