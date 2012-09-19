from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.base import ContentFile
from lhcbPR.models import ResultFile, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler
from django.db import transaction
import json, re, logging

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        """ 
        Pushes the data from the given json file inside the database
        """
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('pushToDB')
        
        myDataDict = {}
        try:
            f = open(args[0],'r').read()
            myDataDict = json.loads(f)
        except ValueError:
            logger.error('Invalid json file!Check your input file\n')
            return
        except IOError:
            logger.error('No such file or directory!\n')
            return
        except IndexError:
            logger.error('No input was given!\n')
            return
        else:
            logger.info('Json file was valid , processing...')
          
        
        try:
            cmtconfigDict = myDataDict['CMTCONFIG']
            mycmtconfig, created = Platform.objects.get_or_create(cmtconfig=cmtconfigDict['platform'])
            
            hostDict = myDataDict['HOST']
            myhost, created = Host.objects.get_or_create(hostname=hostDict['hostname'],
                                                       cpu_info=hostDict['cpu_info'],
                                                       memoryinfo=hostDict['memoryinfo'])
            
            myjobDescription = JobDescription.objects.get(pk=myDataDict['id_jobDescription'])
            
            attributelist = myDataDict['JobAttributes']
            
            if not attributelist:
                logger.warning('No collected results were found in the json input file, perhaps all handlers failed')
                logger.warning('Aborting saving job...')
                return
            
            myjob, created = Job.objects.get_or_create(
                                             host = myhost,
                                             jobDescription = myjobDescription,
                                             platform = mycmtconfig,
                                             time_start = re.sub(',', ' ', myDataDict['time_start']),
                                             time_end = re.sub(',', ' ', myDataDict['time_end']),
                                             status = myDataDict['status']
                                             )
            
            for handres in myDataDict['handlers_info']:
                myHandler = Handler.objects.get(name__exact=handres['handler'])
                handler_result, created = HandlerResult.objects.get_or_create(
                                                                              job=myjob,
                                                                              handler=myHandler,
                                                                              success=handres['successful']
                                                                              )
            
            counter = 0
            for atr in attributelist:
                #logger.info( 'Saving: '+str(counter)+' attribute')
                
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
            
        except KeyError, e:
            logger.error('Attributes given in json file are wrong, aborting...\n'+str(e)+'\n')
            return
        except Exception,e:
            logger.error(Exception)
            logger.error(e)
            logger.error('Aborting...')
            return
            
        
        logger.info('Json data file for new Job added successfully\n')