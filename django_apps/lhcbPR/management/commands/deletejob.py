import os, logging
from tools.cron import CronTab, Event
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from lhcbPR.models import Job

helptext="""

How to use:

    The deletejob command takes exactly one argument as an input,
    the input can be one job id one multiple job ids comma separated.
    Example: python manage.py deletejob 3 or python manage.py deletejob 3,5,6,7,68
    
    The number given as input must be valid job ids(existing job ids), the job ids given
    as input will be deleted from the database.
"""

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        
        if not len(args) == 1 or args[0] == 'help':
            print helptext 
            return
        
        ids = args[0].split(',')
        
        for myid in ids: 
            print Job.objects.get(pk=myid).delete()