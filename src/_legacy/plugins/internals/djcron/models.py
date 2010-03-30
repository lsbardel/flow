from datetime import datetime

from django.db import models

import settings 


class CJob(models.Model):
    last_modified = models.DateTimeField(auto_now = True)
    name          = models.CharField(max_length=100, null = False, unique = True)
    module        = models.CharField(max_length=200, null = False)
    description   = models.TextField(blank = True)
    frequency     = models.CharField(max_length=2, choices = settings.frequencies_tuple)
    clock         = models.DateTimeField()
    
    def __unicode__(self):
        return u'%s' % self.name
        
    class Meta:
        ordering        = ('name',)
        get_latest_by   = "last_modified"
        verbose_name        = 'Cron job'
        verbose_name_plural = 'Cron jobs'