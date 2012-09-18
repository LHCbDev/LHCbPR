from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import ResultRoot, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler
from django.db import transaction
import json, re, logging

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        """ 
        Pushes the data from the given json file inside the database
        """
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('pushFile')
        
        myDataDict = {}
        
        myrootattr, created = JobAttribute.objects.get_or_create(name = 'rootfilesavetest',
                                type = 'rootFile',
                                group = 'root file family',
                                description = 'no description yet',
                                )
        
        #myrootfile. created = ResultRoot.objects.get_or_create(rootfile=args[0])
       