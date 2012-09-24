#!/usr/bin/env python
import os, logging
from optparse import OptionParser, Option, OptionValueError
from datetime import datetime, timedelta
from tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import AddedResults
import pushZip

results_directory = '/afs/cern.ch/user/e/ekiagias/public/database'

logging.root.setLevel(logging.INFO)
logger = logging.getLogger('cronPushToDB')

def pushNewResults():
    #try:
    #    os.chdir(results_directory)
    #except OSError:
    #    logger.error('No such results directory, please check the given directory')
    #    return
    logger.info('Checking results directory for new added zip files...')
    
    list_of_files = os.listdir(results_directory)
    
    for zipResult in list_of_files:
        fileName, fileExtension = os.path.splitext(zipResult)

        results_list = AddedResults.objects.filter(identifier__exact=fileName)
        if not results_list:
            logger.info('New zip founded in results directory, calling pushZip command...')
            pushZip.pushThis(results_directory+os.sep+zipResult)
    
    return

class Command(BaseCommand):

    def handle(self, *args, **options):
    
        c = CronTab(
          Event(pushNewResults, min = range(0,60,1) )
        )
        c.run()