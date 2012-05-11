from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import Handler, JobHandler, JobDescription
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Deleting existing handlers, used for testing
        """
        Handler.objects.all().delete()
        JobHandler.objects.all().delete()
        
        print 'Handlers deleted successfully.'
       