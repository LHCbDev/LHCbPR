import os, logging
from tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from cronPushToDB import pushNewResults
import subprocess

logger = logging.getLogger('mycron')
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
logger.setLevel(logging.INFO)

def cleanHistograms():
    logger.info('Cleaning histogram png path...')
    histograms_png_path = os.path.join(settings.PROJECT_PATH, 'static/images/histograms/*.png')
    #remove histograms.png half day old ( 12 hours ~= 720 minutes )
    subprocess.call( 'find '+histograms_png_path+' -mmin +720 -exec rm {} \;', shell=True)

def logrotatePushToDBlogs():
    """
    /tmp/output.log {
        size 80k
        create 644 ekiagias z5
        rotate 4
    }
    """
    log_file_path = os.path.join(settings.PROJECT_PATH, 'static/logs/adding_results_log')
    mylogrotate_conf_path = os.path.join(settings.PROJECT_PATH, 'static/logs/mylogrotate.conf')
    mylogrotate_conf_status = os.path.join(settings.PROJECT_PATH, 'static/logs/mylogrotate.status')
    mylogrotate_conf = open(mylogrotate_conf_path, 'w')
    mylogrotate_conf.write(log_file_path+' {\nsize 1k\ncreate 744 ekiagias z5\nrotate 4\n}')
    mylogrotate_conf.close()
    
    logger.info('Executing logrotate...')
    subprocess.call('logrotate --state '+mylogrotate_conf_status+' '+mylogrotate_conf_path , shell=True)
    #to be added manually soon
class Command(BaseCommand):

    def handle(self, *args, **options):
    
        logger.info('Starting cronPushToDB...')
        c1 = CronTab(
          Event( pushNewResults, min = range(0,60,1) )
        )
        c1.run()
        
        #run once the day at midnight
        logger.info('Starting cleaning the histograms png path cron job')
        c2 = CronTab(
          Event( cleanHistograms, 0, 0 )
        )
        c2.run()
        
        #run once the day at midnight
        logger.info('Starting logrotate cron job...')
        c3 = CronTab(
          Event( logrotatePushToDBlogs, 0, 0 )
        )
        c3.run()
        
        