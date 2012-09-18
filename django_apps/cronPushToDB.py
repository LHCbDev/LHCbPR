#!/usr/bin/env python
from datetime import datetime, timedelta
from tools.cron import CronTab, Event


def testAction():
    print 'yeah \m/ '+str(datetime.now())

  
def main():
    c = CronTab(
      Event(testAction, min = range(0,60,1) )
    )
    c.run()

if __name__ == "__main__":
    main()