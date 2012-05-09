from xml.etree.ElementTree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from django_apps.generic.models import App, Attr, AppDes, Blob, AppAtr 
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Usage :
            type> python manage.py gen2 path_to_input_file  
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
            gauss_version = myDataDict['gaussVersion']
            pythia_version = myDataDict['pythiaVersion']
            ROOT_version = myDataDict['ROOT_Version']
            eventType = myDataDict['eventType']
            
            if gauss_version == None:
                gauss_version = 'v31r1'
            if pythia_version == None:
                pythia_version = "6.424.2"
                
            application, created = App.objects.get_or_create(appName='Gauss',appVersion=gauss_version)     
            appDescription, created = AppDes.objects.get_or_create(app = application,options=eventType) 
            
            
            for key, value in myDataDict.items():
                if not key == 'gaussVersion' and not key == 'pythiaVersion' and not key == 'histograms' and not key == 'eventType':
                    atr, created = Attr.objects.get_or_create(name=key, type='string')
                    appAtr = AppAtr(appDes = appDescription, attr=atr, value=value)
                    appAtr.save()
            atr, created = Attr.objects.get_or_create(name='pythiaVersion', type='string')
            appAtr = AppAtr(appDes = appDescription, attr=atr , value = pythia_version )
            appAtr.save()
            
            histograms = {}
            histograms = myDataDict['histograms']
            
            for key, value in histograms.items():
                blobb = Blob(appDes = appDescription, name = key, data = value, rootVersion=ROOT_version)
                blobb.save()
            
        except KeyError:
            self.stdout.write('Attributes given in json file are wrong, aborting...\n')
            
        
        self.stdout.write('Json file for generic Job added successfully\n')