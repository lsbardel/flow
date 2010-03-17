from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.utils.text import capfirst
from django.contrib.contenttypes.models import ContentType

        
class Server(models.Model):
    name            = models.CharField(blank  = True, max_length = 60)
    url             = models.CharField(unique = True, max_length = 120)
    description     = models.TextField(blank  = True)
    
    def __unicode__(self):
        if self.name:
            return '%s ( %s )' % (self.name,self.url)
        else:
            return self.url