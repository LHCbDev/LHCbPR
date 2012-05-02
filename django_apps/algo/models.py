from django.db import models

class Algorithm(models.Model):
    alg = models.CharField(max_length=200)
    avg_user = models.FloatField()
    avg_clock = models.FloatField()
    minn = models.FloatField()
    maxn = models.FloatField()
    count = models.IntegerField()
    total = models.FloatField()

    def __unicode__(self):
        return self.alg

class History(models.Model):
    current = models.CharField(max_length=200)
    reference = models.CharField(max_length=200)
    body = models.CharField(max_length=2000)

    def __unicode__(self):
        return self.current+' vs '+self.reference