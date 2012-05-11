from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import Handler, JobHandler, JobDescription
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Addining a handler to a job Description id , used for testing
        """
        myDataDict = {}
    
        jobDescription_id = args[0]
        handler_name = args[1]
        
        handd, created = Handler.objects.get_or_create(name=handler_name,description="")
        jobD = JobDescription.objects.get(pk=jobDescription_id)
        
        handyNew, created = JobHandler.objects.get_or_create(jobDescription=jobD,handler=handd)
       
        print 'Handler added successfully.'