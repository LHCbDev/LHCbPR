from django.db import models

class Job(models.Model):
    eventType = models.CharField(max_length=200)
    gaussVersion = models.CharField(max_length=200)
    pythiaVersion = models.CharField(max_length=200)
    totalCrossSection = models.FloatField()
    bCrossSection = models.FloatField()
    cCrossSection = models.FloatField()
    promptCharmCrossSection = models.FloatField()
    totalAcceptedEvents = models.IntegerField()
    signalProcessCrossSection = models.FloatField()
    signalProcessFromBCrossSection = models.FloatField()
    generatorLevelCutEfficiency = models.FloatField()
    timePerEvent = models.FloatField()

    def __unicode__(self):
        return 'Gauss '+self.gaussVersion+' eventtype '+self.eventType

class Histos(models.Model):    
    job = models.ForeignKey(Job)
    name = models.CharField(max_length=200)
    data = models.TextField()
    
    def __unicode__(self):
        return 'name '+self.name
    
