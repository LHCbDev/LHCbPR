from django.core.management.base import BaseCommand, CommandError
from lhcbPR.models import Application, Options, JobDescription

class Command(BaseCommand):
    """
    Just a test to initialize some demo jobDescriptions
    pk=1(primarykey=1) for Brunel v42r0p1
    and pk=2 for Gauss v41r2
    """

    def handle(self, *args, **options):
        app, created = Application.objects.get_or_create(appName='Brunel',appVersion='v42r0p1')
        jobDescr = JobDescription.objects.get_or_create(application=app)
        
        app2, created = Application.objects.get_or_create(appName='Gauss',appVersion='v41r2')
        jobDescr2 = JobDescription.objects.get_or_create(application=app2)
        
        app3, created = Application.objects.get_or_create(appName='Gauss',appVersion='v42r0')
        jobDescr3 = JobDescription.objects.get_or_create(application=app3)
        
        print 'Test job descriptions added.'
           
            
        