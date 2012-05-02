from algo.models import Algorithm
from django.views.decorators.csrf import csrf_exempt    
from xml.etree.ElementTree import ElementTree
from django.core.management.base import BaseCommand, CommandError
from database_test.algo.models import Algorithm
from xml.parsers.expat import ExpatError

class Command(BaseCommand):

    def handle(self, *args, **options):
        """ 
        Usage :
            type> python manage.py insert path_to_input_file/files  
        """
        tree = ElementTree()
        #'/afs/cern.ch/user/e/ekiagias/workspace/database_test/database_test/inputs/results.xml'
        try:
            tree.parse(args[0])
        except ExpatError:
            self.stdout.write('Invalid xml file!Check your syntax\n')
            return
        except IOError:
            self.stdout.write('No such file or directory!\n')
            return
        except IndexError:
            self.stdout.write('No input was given!\n')
            return
        else:
            self.stdout.write('XML file is valid , processing...\n')
          
        #empty dictonary which is going
        #to contain the input data
        input = {}
        
        for parent in tree.getiterator("alg"):
            input[parent.tag] = parent.attrib.get("name")
            for child in parent:
                input[child.tag] = child.text
        
            al=Algorithm(alg=input['alg'],avg_user=input['avg_user'],avg_clock=input['avg_clock'],\
                     minn=input['min'],maxn=input['max'],count=input['count'],total=input['total'])
            al.save()
            input.clear()
        
        self.stdout.write('XML attributes added successfully\n')