#!/usr/bin/env python
import os, logging
from optparse import OptionParser, Option, OptionValueError
from datetime import datetime, timedelta
from tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from lhcbPR.models import AddedResults
import pushZip

#results_directory = '/afs/cern.ch/user/e/ekiagias/public/database'
results_directory = os.path.join(settings.PROJECT_PATH, 'static/uploaded')
logging.root.setLevel(logging.INFO)
logger = logging.getLogger('cronPushToDB')

def pushNewResults():
    log_file_path = os.path.join(settings.PROJECT_PATH, 'static/logs/adding_results')
    
    logfile = open(log_file_path, 'a')
    if not os.path.isdir(results_directory):
        logger.error(str(datetime.now())+': No such results directory, please check the given directory')
        logfile.write(str(datetime.now())+': No such results directory, please check the given directory\n')
        return
    
    logger.info(str(datetime.now())+': Checking results directory for new added zip files...')
    logfile.write(str(datetime.now())+': Checking results directory for new added zip files...\n')
    
    list_of_files = os.listdir(results_directory)
    
    for zipResult in list_of_files:
        fileName, fileExtension = os.path.splitext(zipResult)

        results_list = AddedResults.objects.filter(identifier__exact=fileName)
        if not results_list:
            logger.info(str(datetime.now())+': New zip founded in results directory, calling pushZip command...')
            logfile.write(str(datetime.now())+': New zip founded in results directory, calling pushZip command...\n')
            pushZip.pushThis(results_directory+os.sep+zipResult)

class Command(BaseCommand):

    def handle(self, *args, **options):
    
        c = CronTab(
          Event(pushNewResults, min = range(0,60,1) )
        )
        c.run()