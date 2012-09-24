#!/usr/bin/env python
import os, logging
from optparse import OptionParser, Option, OptionValueError
from datetime import datetime, timedelta
from tools.cron import CronTab, Event

results_directory = '/afs/cern.ch/user/e/ekiagias/public/database'

logging.root.setLevel(logging.WARNING)
logger = logging.getLogger('collectRunResults.py')

def pushNewResults():
    try:
        os.chdir(results_directory)
    except OSError:
        logger.error('No such results directory, please check the given directory')
        return
    
    print os.listdir(results_directory)
        

def main():
    description = """Only quiet lame argument, that's all """
    parser = OptionParser(usage='usage: %prog [options]',
                          description=description)
    parser.add_option("-q", "--quiet", action="store_true",
                      dest="ssss", default=False,
                      help="Just be quiet (do not print info from logger)")
    options, args = parser.parse_args()
    
    if not options.ssss:
        logging.root.setLevel(logging.INFO)
    
    c = CronTab(
      Event(pushNewResults, min = range(0,60,1) )
    )
    c.run() 

if __name__ == "__main__":
    main()