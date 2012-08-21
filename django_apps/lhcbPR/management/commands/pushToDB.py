from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription
from django.db import transaction
import json, re

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        """ 
        Pushes the data from the given json file inside the database
        """
        myDataDict = {}
        try:
            f = open(args[0],'r').read()
            myDataDict = json.loads(f)
        except ValueError:
            self.stdout.write('Invalid json file!Check your input file\n')
            return
        except IOError:
            self.stdout.write('No such file or directory!\n')
            return
        except IndexError:
            self.stdout.write('No input was given!\n')
            return
        else:
            self.stdout.write('Json file was valid , processing...\n')
          
        
        try:
            cmtconfigDict = myDataDict['CMTCONFIG']
            mycmtconfig, created = Platform.objects.get_or_create(cmtconfig=cmtconfigDict['platform'])
            
            hostDict = myDataDict['HOST']
            myhost, created = Host.objects.get_or_create(hostname=hostDict['hostname'],
                                                       cpu_info=hostDict['cpu_info'],
                                                       memoryinfo=hostDict['memoryinfo'])
            
            myjobDescription = JobDescription.objects.get(pk=myDataDict['id_jobDescription'])
            
            
            myjob, created = Job.objects.get_or_create(
                                             host = myhost,
                                             jobDescription = myjobDescription,
                                             platform = mycmtconfig,
                                             time_start = re.sub(',', ' ', myDataDict['time_start']),
                                             time_end = re.sub(',', ' ', myDataDict['time_end']),
                                             status = myDataDict['status']
                                             )
            
            attributelist = myDataDict['JobAttributes']
            counter = 0
            for atr in attributelist:
                self.stdout.write( 'Saving: '+str(counter)+' attribute\n')
                myAtr, created = JobAttribute.objects.get_or_create(
                                                                    name = atr['name'],
                                                                    type = atr['type'],
                                                                    description = atr['description'],
                                                                    group = atr['group']
                                                                    )
                if atr['type'] == 'Float':
                    finalAtr= ResultFloat.objects.get_or_create(
                                                    job = myjob,
                                                    jobAttribute = myAtr,
                                                    data = atr['data']
                                                    ) 
                elif atr['type'] == 'Integer':
                    finalAtr = ResultInt.objects.get_or_create(
                                                    job = myjob,
                                                    jobAttribute = myAtr,
                                                    data = atr['data']
                                                    ) 
                elif atr['type'] == 'String':
                    finalAtr = ResultString.objects.get_or_create(
                                                    job = myjob,
                                                    jobAttribute = myAtr,
                                                    data = atr['data']
                                                    ) 
                elif atr['type'] == 'ROOT_Blob':
                    finalAtr, created = ResultBinary.objects.get_or_create(
                                                    job = myjob,
                                                    jobAttribute = myAtr,
                                                    data = atr['data'],
                                                    root_version = atr['ROOT_version']
                                                    ) 
                
                counter+=1
            
        except KeyError:
            self.stdout.write('Attributes given in json file are wrong, aborting...\n')
            
        
        self.stdout.write('Json data file for new Job added successfully\n')