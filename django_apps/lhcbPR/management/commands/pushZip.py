from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.base import ContentFile
from lhcbPR.models import AddedResults, ResultFile, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler
from django.db import transaction
import json, re, logging, zipfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('pushZip')

def pushThis(zipFile):
    myDataDict = {}
    try:
        unzipper = zipfile.ZipFile(zipFile)
        
        myDataDict = json.loads(unzipper.read('json_results'))
    except ValueError:
        logger.error('Invalid json file in zip folder!Check your input zip folder\n')
        return
    except IOError,e:
        logger.error('No such file or directory!\n')
        print str(e)
        return
    except IndexError:
        logger.error('No input was given!\n')
        return
    except Exception, e:
        logger.error(str(Exception))
    else:
        logger.info('Json file from zip folder was valid , processing...')
      
    
    try:
        results_unique_id, created = AddedResults.objects.get_or_create(identifier=myDataDict['results_id'])
        if not created:
            logger.warning('Results file '+results_unique_id.identifier+' already added, aborting...')
            return
        
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
                                         status = myDataDict['status'],
                                         success = True
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
            elif atr['type'] == 'File':
                file = unzipper.read(atr['filename'])
                finalAtr = ResultFile(
                                      job = myjob,
                                      jobAttribute = myAtr,
                                      )
                finalAtr.file.save(atr['filename'], ContentFile(file), save=True)
            
            counter+=1
     
        logger.info('Zip folder with new job results added successfully\n')
        return
    
    except KeyError, e:
        logger.error('Attributes given in json file are wrong, aborting...\n'+str(e)+'\n')
        return
    except Exception,e:
        logger.error(e)
        logger.error('Aborting...')
        return

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        """ 
        Pushes the data from the given json file inside the database
        """
        
        zipFile = args[0]
        
        pushThis(zipFile)
        return