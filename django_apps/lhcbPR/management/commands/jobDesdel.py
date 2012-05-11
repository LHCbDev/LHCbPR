from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import Application, Options, JobDescription

class Command(BaseCommand):
    """
    Command to delete existing job descriptions , used for testing
    """

    def handle(self, *args, **options):
        JobDescription.objects.all().delete()
        Application.objects.all().delete()
        Options.objects.all().delete()
        
        print 'Test job descriptions deleted.'
           
            
        