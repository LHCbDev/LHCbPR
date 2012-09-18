from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import JobHandler, Application, Requested_platform, Options, Platform, Host, Job, JobResults, JobAttribute, ResultString, ResultInt, ResultFloat, ResultBinary, JobDescription, HandlerResult, Handler, SetupProject
from django.db import transaction
import json, re, logging

class Command(BaseCommand):

    @transaction.commit_on_success
    def handle(self, *args, **options):
        
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('myloaddata')
        
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
        
        counter=0  
        for obj in json.loads(f):
            if obj['model'] == 'lhcbPR.host':
                Host.objects.get_or_create(
                                           pk=obj['pk'],
                                           cpu_info=obj['fields']['cpu_info'],
                                           hostname=obj['fields']['hostname'],
                                           memoryinfo=obj['fields']['memoryinfo']
                                           )
                logger.info('Host saved '+str(counter))
            if obj['model'] == 'lhcbPR.application':
                Application.objects.get_or_create(
                                           pk=obj['pk'],
                                           appVersion=obj['fields']['appVersion'],
                                           appName=obj['fields']['appName'],
                                           )
                logger.info('Application saved '+str(counter))
            if obj['model'] == 'lhcbPR.options':
                Options.objects.get_or_create(
                                           pk=obj['pk'],
                                           content=obj['fields']['content'],
                                           description=obj['fields']['description'],
                                           )
                logger.info('Options saved '+str(counter))
            if obj['model'] == 'lhcbPR.setupproject':
                SetupProject.objects.get_or_create(
                                           pk=obj['pk'],
                                           content=obj['fields']['content'],
                                           description=obj['fields']['description'],
                                           )
                logger.info('SetupProject saved '+str(counter))
            if obj['model'] == 'lhcbPR.jobdescription':
                try:
                    setupTemp = SetupProject.objects.get(pk=obj['fields']['setup_project'])
                    
                    JobDescription.objects.get_or_create(
                                               pk=obj['pk'],
                                               application=Application.objects.get(pk=obj['fields']['application']),
                                               options=Options.objects.get(pk=obj['fields']['options']),
                                               setup_project=setupTemp
                                               )
                except Exception:
                    JobDescription.objects.get_or_create(
                                               pk=obj['pk'],
                                               application=Application.objects.get(pk=obj['fields']['application']),
                                               options=Options.objects.get(pk=obj['fields']['options']),
                                               )
                logger.info('JobDescription saved '+str(counter))
            if obj['model'] == 'lhcbPR.platform':
                Platform.objects.get_or_create(
                                           pk=obj['pk'],
                                           cmtconfig=obj['fields']['cmtconfig'],
                                           )
                logger.info('Platform saved '+str(counter))
            if obj['model'] == 'lhcbPR.requested_platform':
                Requested_platform.objects.get_or_create(
                                           pk=obj['pk'],
                                           jobdescription=JobDescription.objects.get(pk=int(obj['fields']['jobdescription'])),
                                           cmtconfig=Platform.objects.get(pk=obj['fields']['cmtconfig']),
                                           )
                logger.info('Requested_platform saved '+str(counter))
            if obj['model'] == 'lhcbPR.job':
                Job.objects.get_or_create(
                                           pk=obj['pk'],
                                           host=Host.objects.get(pk=obj['fields']['host']),
                                           jobDescription=JobDescription.objects.get(pk=obj['fields']['jobDescription']),
                                           platform=Platform.objects.get(pk=obj['fields']['platform']),
                                           status=obj['fields']['status'],
                                           time_end=obj['fields']['time_end'],
                                           time_start=obj['fields']['time_start']
                                           )
                logger.info('Job saved '+str(counter))
            if obj['model'] == 'lhcbPR.handler':
               Handler.objects.get_or_create(
                                           pk=obj['pk'],
                                           description=obj['fields']['description'],
                                           name=obj['fields']['name'],
                                           )
               logger.info('Handler saved '+str(counter))
            if obj['model'] == 'lhcbPR.jobhandler':
               JobHandler.objects.get_or_create(
                                           pk=obj['pk'],
                                           handler=Handler.objects.get(pk=obj['fields']['handler']),
                                           jobDescription=JobDescription.objects.get(pk=obj['fields']['jobDescription']),
                                           )
               logger.info('JobHandler saved '+str(counter))
            #if obj['model'] == 'lhcbPR.jobattribute':
            #   JobAttribute.objects.get_or_create(
            #                               pk=obj['pk'],
            #                               description=obj['fields']['description'], 
            #                               group=obj['fields']['group'], 
            #                               name=obj['fields']['name'], 
            #                               type=obj['fields']['type']
            #                               )
            #   logger.info('JobAttribute saved '+str(counter))
            #if obj['model'] == 'lhcbPR.jobresults':
            #   JobResults.objects.get_or_create(
            #                               pk=obj['pk'],
            #                               job=Job.objects.get(pk=obj['fields']['job']),
            #                               jobAttribute=JobAttribute.objects.get(pk=obj['fields']['jobAttribute']),
            #                               )
            #   logger.info('JobResults saved '+str(counter))
            #if obj['model'] == 'lhcbPR.resultstring':
            #   ResultString.objects.get_or_create(
            #                               pk=obj['pk'],
            #                               data=obj['fields']['data'],
            #                               )
            #   logger.info('ResultString saved '+str(counter))
            #if obj['model'] == 'lhcbPR.resultint':
            #   ResultInt.objects.get_or_create(
            #                               pk=obj['pk'],
            #                               data=obj['fields']['data'],
            #                               )
            #   logger.info('ResultInt saved '+str(counter))
            #if obj['model'] == 'lhcbPR.resultfloat':
            #   ResultFloat.objects.get_or_create(
            #                               pk=obj['pk'],
            #                               data=obj['fields']['data'],
            #                               )
            #   logger.info('ResultFloat saved '+str(counter))
            if obj['model'] == 'lhcbPR.handlerresult':
               HandlerResult.objects.get_or_create(
                                           pk=obj['pk'],
                                           handler=Handler.objects.get(pk=obj['fields']['handler']),
                                           job=Job.objects.get(pk=obj['fields']['job']),
                                           success=obj['fields']['success']
                                           )
               logger.info('HandlerResult saved '+str(counter))
            counter+=1
            
               
        logger.info('Json file was saved successfully')