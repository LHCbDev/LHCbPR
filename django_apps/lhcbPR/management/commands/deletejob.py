from django.core.management.base import BaseCommand
from django.db import transaction
from lhcbPR.models import Job

helptext="""

How to use:

    The deletejob command takes exactly one argument as an input,
    the input can be one job id one multiple job ids comma separated.
    Example: 
        ./manage.py deletejob 3
        ./python manage.py deletejob 3,5,6,7,68
    
    The number given as input must be valid job ids(existing job ids), the job ids given
    as input will be deleted from the database.
"""

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        
        if not len(args) == 1 or args[0] == 'help' or args[0] == '--help':
            print helptext 
            return
        
        ids = args[0].split(',')
        
        for myid in ids: 
            print Job.objects.get(pk=myid).delete()
            
        print 'Jobs deleted successfully'