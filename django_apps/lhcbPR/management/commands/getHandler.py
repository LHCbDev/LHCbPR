from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import JobHandler, JobDescription

class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Gets a job description id and return the name of the proper
        handler to handle this job id
        """
        jobDes = JobDescription.objects.get(pk=args[0])
        handy = JobHandler.objects.filter(jobDescription=jobDes)[0]
        
        return handy.handler.name
        
       