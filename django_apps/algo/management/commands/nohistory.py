from django.core.management.base import BaseCommand, CommandError
from algo.models import History

class Command(BaseCommand):

    def handle(self, *args, **options):
        if History.objects.all().count() == 0:
            self.stdout.write('History is already empty!\n') 
        elif History.objects.all().count > 0:
            History.objects.all().delete()
            self.stdout.write('History cleared.\n')
           