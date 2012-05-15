from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import CMTCONFIG, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription
import json, re

class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Return the average value of a variable, takes teh jobdescription id 
        and the name of the variable(used for testing)
        """
        if not len(args) == 2:
            self.stdout.write('Wrong input, try again: command id attribute_name')
        
         
        myjobs = Job.objects.filter(jobDescription__id=args[0]).values('id').distinct('id')
        myatr = JobAttribute.objects.get(name=args[1])
        
        sum = 0
        jobs_number = len(myjobs)
        for jobb in myjobs:
            
            variable = JobResults.objects.get(job__id=jobb['id'],jobAttribute__id=myatr.id)
            
            if variable.jobAttribute.type == 'Float':
                sum+= variable.resultfloat.data
            elif variable.jobAttribute.type == 'Integer':
                sum+= variable.resultint.data
            elif variable.jobAttribute.type == 'String':
                sum+= variable.resultstring.data
        
        self.stdout.write('Average of: '+args[1]+' is: '+str(sum/jobs_number)+'\n')