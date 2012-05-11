from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=50)
    cpu_info = models.CharField(max_length=200)
    memoryinfo = models.CharField(max_length=200)

    def __unicode__(self):
        return self.hostname

class CMTCONFIG(models.Model):
    platform = models.CharField(max_length=100)

    
class Application(models.Model):
    appName = models.CharField(max_length=50)
    appVersion = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('appName', 'appVersion',)

    def __unicode__(self):
        return self.appName+' '+self.appVersion

class Options(models.Model):
    pass

class JobDescription(models.Model):
    application = models.ForeignKey(Application)
    options = models.ForeignKey(Options,null=True) 
    
class Job(models.Model):
    host = models.ForeignKey(Host,null=True)
    jobDescription = models.ForeignKey(JobDescription)
    platform = models.ForeignKey(CMTCONFIG,null=True)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    status = models.CharField(max_length=50)
 
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
    root_version = models.CharField(max_length=20)
    data = models.TextField()