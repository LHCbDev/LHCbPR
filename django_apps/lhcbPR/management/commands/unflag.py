from django.core.management.base import BaseCommand
from django.db import transaction
from lhcbPR.models import Job

helptext="""

How to use:

    The flag command takes exactly one argument as an input,
    the input can be one job id one multiple job ids comma separated.
    Example: 
        ./manage.py unflag 2067
        ./manage.py unflag 10,8,6,54,6
    
    The number given as input must be valid job ids(existing job ids), the job ids given
    as input will be flagged as successful in the database.
"""

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        
        if not len(args) == 1 or args[0] == 'help':
            print helptext 
            return
        
        ids = args[0].split(',')
        
        for myid in ids: 
            job_temp = Job.objects.get(pk=myid)
            job_temp.success = True
            job_temp.save()
            
            
        print 'Jobs flagged as successful, successfully'