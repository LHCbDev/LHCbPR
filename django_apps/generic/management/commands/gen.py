from xml.etree.ElementTree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from database_test.genplot.models import Job, Histos
import json


class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Usage :
            type> python manage.py gen path_to_input_file  
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
            
            if gauss_version == None:
                gauss_version = 'v31r1'
            if pythia_version == None:
                pythia_version = "6.424.2"
            
                      
            jobgauss = Job(
                eventType = myDataDict['eventType'], 
                gaussVersion = gauss_version, 
                pythiaVersion = pythia_version, 
                totalCrossSection = float(myDataDict['totalCrossSection']), 
                bCrossSection = float(myDataDict['bCrossSection']), 
                cCrossSection = float(myDataDict['cCrossSection']), 
                promptCharmCrossSection = float(myDataDict['promptCharmCrossSection']),
                totalAcceptedEvents = int(myDataDict['totalAcceptedEvents']), 
                signalProcessCrossSection = float(myDataDict['signalProcessCrossSection']), 
                signalProcessFromBCrossSection = float(myDataDict['signalProcessFromBCrossSection']), 
                generatorLevelCutEfficiency = float(myDataDict['generatorLevelCutEfficiency']) , 
                timePerEvent = float(myDataDict['timePerEvent']))
            
            jobgauss.save()
            
            histograms = {}
            histograms = myDataDict['histograms']
            
            for key, value in histograms.items():
                hist = Histos(job = jobgauss, name = key, data = value)
                hist.save()
            
        except KeyError:
            self.stdout.write('Attributes given in json file are wrong, aborting...\n')
            
        
        self.stdout.write('Json file for Job added successfully\n')