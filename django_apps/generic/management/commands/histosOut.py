from django.core.management.base import BaseCommand, CommandError
from genplot.models import Job, Histos
import json
class Command(BaseCommand):

    def handle(self, *args, **options):
        current_event = args[0]
        reference_event = args[1]
        outputfile = args[2]
        
        cDict = {}
        current = Job.objects.get(eventType__exact=current_event)
        current_histos = Histos.objects.all().filter(job__exact=current)
        
        for cur in current_histos:
            cDict[cur.name]=cur.data
            print cur.name+" cur "
        
        rDict = {}
        reference = Job.objects.get(eventType__exact=reference_event)
        reference_histos = Histos.objects.all().filter(job__exact=reference)
        
        for ref in reference_histos:
            rDict[ref.name]=ref.data
            print ref.name+" ref"
        
        gloDict = {}
        
        gloDict['current']= cDict
        gloDict['reference'] = rDict
        
        f = open(outputfile,'w')
        f.write(json.dumps(gloDict))
        
        
        
        