from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=50)
    cpu_info = models.CharField(max_length=200)
    memoryinfo = models.CharField(max_length=200)

    def __unicode__(self):
        return self.hostname
 
class Application(models.Model):
    appName = models.CharField(max_length=50, db_index=True)
    appVersion = models.CharField(max_length=50, db_index=True)
    
    class Meta:
        unique_together = ('appName', 'appVersion',)

    def __unicode__(self):
        return self.appName+' '+self.appVersion

class Options(models.Model):
    content = models.CharField(max_length=2000)
    description = models.CharField(max_length=2000, db_index=True)

class SetupProject(models.Model):
    content = models.CharField(max_length=200)
    description = models.CharField(max_length=200, db_index=True)

class JobDescription(models.Model):
    application = models.ForeignKey(Application)
    options = models.ForeignKey(Options,null=True)
    setup_project = models.ForeignKey(SetupProject,null=True) 

class Platform(models.Model):
    cmtconfig = models.CharField(max_length=100)

class Requested_platform(models.Model):
    jobdescription = models.ForeignKey(JobDescription)
    cmtconfig = models.ForeignKey(Platform)
    
class Job(models.Model):
    host = models.ForeignKey(Host,null=True)
    jobDescription = models.ForeignKey(JobDescription)
    platform = models.ForeignKey(Platform,null=True)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    status = models.CharField(max_length=50)
    
class Handler(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
class JobHandler(models.Model):
    jobDescription = models.ForeignKey(JobDescription)
    handler = models.ForeignKey(Handler)
 
class JobAttribute(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=20)
    group = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    
class JobResults(models.Model):
    job = models.ForeignKey(Job)
    jobAttribute = models.ForeignKey(JobAttribute)
    
class ResultString(JobResults):
    data = models.CharField(max_length=100)
    
class ResultFloat(JobResults):
    data = models.FloatField()  
    
class ResultInt(JobResults):
    data = models.IntegerField()
    
class ResultBinary(JobResults):
    data = models.TextField()
    

def content_file_name(instance, filename):
    return '/'.join([str(instance.job.jobDescription.pk), str(instance.job.pk), filename])

class ResultFile(JobResults):
    file = models.FileField(upload_to=content_file_name,blank=True)


class HandlerResult(models.Model):
    job = models.ForeignKey(Job)
    handler = models.ForeignKey(Handler)
    success = models.BooleanField()
    
class AddedResults(models.Model):
    identifier = models.CharField(max_length=64)