from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.core.files.base import ContentFile
from lhcbPR.models import AddedResults, ResultFile, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler
from django.db import transaction
import json, re, logging, zipfile, os, sys
from django.conf import settings

#get the logger from the django settings
logger = logging.getLogger('push_logger')
log = ''

def pushThis(zipFile):
    DataDict = {}
    try:
        head, tail = os.path.split(zipFile)
        log = "[ 'zipFile' : '{0}' ]  ".format(tail)
        unzipper = zipfile.ZipFile(zipFile)
        
        DataDict = json.loads(unzipper.read('json_results'))
    except ValueError, e:
        logger.exception("{0} exception occurred ".format(log))
        sys.exit(1)
    except IOError,e:
        logger.exception("{0} exception occurred ".format(log))
        sys.exit(1)
    except IndexError, e:
        logger.exception("{0} exception occurred ".format(log))
        sys.exit(1)
    except Exception, e:
        logger.exception("{0} exception occurred ".format(log))
        sys.exit(1)
    
    try:
        results_unique_id, created = AddedResults.objects.get_or_create(identifier=DataDict['results_id'])
        if not created:
            log+= 'Results zip file {0} already added, aborting...'.format(results_unique_id.identifier)
            logger.warning(log)
            return
        
        log+= " [ 'job_description_id' : {0} ] ".format(DataDict['id_jobDescription'])
        log+= " [ 'host' : '{0}' ]".format(DataDict['HOST']['hostname'])
        log+= " [ 'platform' : '{0}' ] ".format(DataDict['CMTCONFIG']['platform'])
        log+= " [ 'time_start' : '{0}' ] ".format(DataDict['time_start'])
        
        cmtconfigDict = DataDict['CMTCONFIG']
        mycmtconfig, created = Platform.objects.get_or_create(cmtconfig=cmtconfigDict['platform'])
        
        hostDict = DataDict['HOST']
        myhost, created = Host.objects.get_or_create(hostname=hostDict['hostname'],
                                                   cpu_info=hostDict['cpu_info'],
                                                   memoryinfo=hostDict['memoryinfo'])
        
        myjobDescription = JobDescription.objects.get(pk=DataDict['id_jobDescription'])
        
        attributelist = DataDict['JobAttributes']
        
        if not attributelist:
            log+= " No collected results were found in the json_results file, perhaps all handlers failed! Aborting saving job..."
            logger.error(log)
            return
        
        myjob, created = Job.objects.get_or_create(
                                         host = myhost,
                                         jobDescription = myjobDescription,
                                         platform = mycmtconfig,
                                         time_start = re.sub(',', ' ', DataDict['time_start']),
                                         time_end = re.sub(',', ' ', DataDict['time_end']),
                                         status = DataDict['status'],
                                         success = True
                                         )
        
        for handres in DataDict['handlers_info']:
            myHandler = Handler.objects.get(name__exact=handres['handler'])
            handler_result, created = HandlerResult.objects.get_or_create(
                                                                          job=myjob,
                                                                          handler=myHandler,
                                                                          success=handres['successful']
                                                                          )

        for atr in attributelist:
            
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
     
        log+="[ 'job_id' : {0} ]".format(myjob.id)
        logger.info(log+' Zip folder with new job results added successfully\n')
        return
    
    except Exception,e:
        logger.exception(log+' exception occurred!')
        sys.exit(1)

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        """ 
        Pushes the data from the given json file inside the database
        """
        zipFile = args[0]
        pushThis(zipFile)
        return