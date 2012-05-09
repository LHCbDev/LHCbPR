from django.core.management.base import BaseCommand, CommandError
from generic.models import App, AppDes, Attr, Blob, AppAtr

class Command(BaseCommand):

    def handle(self, *args, **options):
        if App.objects.all().count() == 0 and AppAtr.objects.all().count() == 0 and AppDes.objects.all().count() == 0 and Attr.objects.all().count() == 0 and Blob.objects.all().count() == 0:
            self.stdout.write('There are no generic jobs in the database.\n') 
        elif App.objects.all().count() > 0 or AppAtr.objects.all().count() > 0 or AppDes.objects.all().count() > 0 or Attr.objects.all().count() > 0 or Blob.objects.all().count() > 0:
            App.objects.all().delete()
            AppAtr.objects.all().delete()
            AppDes.objects.all().delete()
            Attr.objects.all().delete()
            Blob.objects.all().delete()
            self.stdout.write('All generic stuff deleted.\n')
           
            
        