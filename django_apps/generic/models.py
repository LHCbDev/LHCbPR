from django.db import models

#App = Application
class App(models.Model):
    appName = models.CharField(max_length=50)
    appVersion = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('appName', 'appVersion',)

    def __unicode__(self):
        return self.appName+' '+self.appVersion

#AppDes = Application Description
class AppDes(models.Model):
    app = models.ForeignKey(App)
    options = models.CharField(max_length=100)

    def __unicode__(self):
        return self.app.appName+' '+self.app.appVersion+' '+self.options
    
#Attr = Attribute
class Attr(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    
    class Meta:
        unique_together = ('name', 'type',)

    def __unicode__(self):
        return self.name+' '+self.type

#Blob = Blob (captain obvious)
class Blob(models.Model):
    appDes = models.ForeignKey(AppDes)
    name = models.CharField(max_length=50)
    data = models.TextField()
    rootVersion = models.CharField(max_length=50)

#AppAtr = Application Attributes 
class AppAtr(models.Model):
    appDes =  models.ForeignKey(AppDes)
    attr = models.ForeignKey(Attr) 
    value = models.CharField(max_length=50) 