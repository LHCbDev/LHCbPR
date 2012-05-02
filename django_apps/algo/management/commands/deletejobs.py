from django.core.management.base import BaseCommand, CommandError
from genplot.models import  Histos, Job

class Command(BaseCommand):

    def handle(self, *args, **options):
        if Job.objects.all().count() == 0:
            self.stdout.write('There are no Jobs in the database.\n') 
        elif Job.objects.all().count > 0:
            Job.objects.all().delete()
            Histos.objects.all().delete()
            self.stdout.write('All jobs are deleted.\n')
           
            
        