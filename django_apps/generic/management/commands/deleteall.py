from django.core.management.base import BaseCommand, CommandError
from algo.models import Algorithm

class Command(BaseCommand):

    def handle(self, *args, **options):
        if Algorithm.objects.all().count() == 0:
            self.stdout.write('There are no algorithms in the database.\n') 
        elif Algorithm.objects.all().count > 0:
            Algorithm.objects.all().delete()
            self.stdout.write('All algorithms deleted.\n')
           
            
        