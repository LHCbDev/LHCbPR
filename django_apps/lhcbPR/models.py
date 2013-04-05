from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=50)
    cpu_info = models.CharField(max_length=200)
    memoryinfo = models.CharField(max_length=200)

    def __unicode__(self):
        return self.hostname
 
class Application(models.Model):
    appName = models.CharField(max_length=50)
    appVersion = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('appName', 'appVersion',)

    def __unicode__(self):
        return '{0}  {1}'.format(self.appName, self.appVersion)

class Options(models.Model):
    content = models.CharField(max_length=2000)
    description = models.CharField(max_length=2000)
    
    def __unicode__(self):
        return self.description

class SetupProject(models.Model):
    content = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.description

class JobDescription(models.Model):
    application = models.ForeignKey(Application, related_name='jobdescriptions')
    options = models.ForeignKey(Options,null=True, related_name='jobdescriptions')
    setup_project = models.ForeignKey(SetupProject,null=True, related_name='jobdescriptions') 
    
    def __unicode__(self):
        return '{0} (id)   {1}  {2}  {3}'.format(self.id ,self.application.appName, self.application.appVersion, self.options.description)

class Platform(models.Model):
    cmtconfig = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.cmtconfig

class Requested_platform(models.Model):
    jobdescription = models.ForeignKey(JobDescription)
    cmtconfig = models.ForeignKey(Platform)
    
    def __unicode__(self):
        return '{0} (job_description_id)   ---   {1}'.format(self.jobdescription.id, self.cmtconfig)
    
class Job(models.Model):
    host = models.ForeignKey(Host,null=True, related_name='jobs')
    jobDescription = models.ForeignKey(JobDescription, related_name='jobs')
    platform = models.ForeignKey(Platform,null=True, related_name='jobs')
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    status = models.CharField(max_length=50)
    success = models.NullBooleanField()
    
    def __unicode__(self):
        return '{0} (id) -- {1} (job_description_id)  ---  {2}  ---  {3}  ---  {4} --- {5}'.format(
                    self.id, self.jobDescription.id, self.time_end, 
                    self.platform.cmtconfig, self.host.hostname, self.success)
    
class Handler(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
    
class JobHandler(models.Model):
    jobDescription = models.ForeignKey(JobDescription)
    handler = models.ForeignKey(Handler)
    
    def __unicode__(self):
        return '{0} (job_description_id) -- -- {1}'.format(self.jobDescription.id, self.handler)
 
class JobAttribute(models.Model):
    name = models.CharField(max_length=500)
    type = models.CharField(max_length=200)
    group = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    
    def __unicode__(self):
        return '{0} (id)  {1}  --  {2}  {3}'.format(self.id, self.name, self.type, self.description)
    
class JobResults(models.Model):
    job = models.ForeignKey(Job, related_name='jobresults')
    jobAttribute = models.ForeignKey(JobAttribute, related_name='jobresults')
    
    def __unicode__(self):
        return '{0} (job_id) --- {1} (jobAttribute_id)'.format(self.job.id, self.jobAttribute.id)
    
class ResultString(JobResults):
    data = models.CharField(max_length=100)
    
class ResultFloat(JobResults):
    data = models.FloatField()  
    
class ResultInt(JobResults):
    data = models.IntegerField()
        
def content_file_name(instance, filename):
    return '/'.join([str(instance.job.jobDescription.pk), str(instance.job.pk), filename])

class ResultFile(JobResults):
    file = models.FileField(upload_to=content_file_name,blank=True)

class HandlerResult(models.Model):
    job = models.ForeignKey(Job)
    handler = models.ForeignKey(Handler)
    success = models.BooleanField()
    
    def __unicode__(self):
        return '{0} (job_id) {1} --- {2}'.format(self.job.id, self.handler.name, self.success)
    
class AddedResults(models.Model):
    identifier = models.CharField(max_length=64)
    
    def __unicode__(self):
        return self.identifier