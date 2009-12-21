from datetime import date

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.utils.text import capfirst
from django.contrib.contenttypes.models import ContentType

from flowrepo.models import Report
from flowrepo.settings import FLOWREPO_DATE_FORMAT

from jflow.db.utils import dict_from_choices

event_type_choices = (
                      (0,_('undefined')),
                      (1,_('meeting')),
                      (2,_('conference call')),
                      (3,_('release')),
                      )

event_type_dict = dict_from_choices(event_type_choices)


class CalendarEvent(models.Model):
    dt              = models.DateField(_('event date'), default=date.today)
    type            = models.IntegerField(_('event_type'), choices=event_type_choices, default=1)
    report          = models.OneToOneField(Report, blank = True, null = True)
    
    def __unicode__(self):
        return '%s - %s' % (self.descriptive_type(),self.dt.strftime(FLOWREPO_DATE_FORMAT))
    
    def descriptive_type(self):
        return capfirst(force_unicode(event_type_dict.get(self.type,'undefined')))
        
    class Meta:
        ordering      = ('-dt',)
        get_latest_by = 'dt'
        
        
class Logger(models.Model):
    last_modified   = models.DateTimeField(auto_now = True)
    created         = models.DateTimeField(auto_now_add = True)
    relevant_date   = models.DateField()
    updated         = models.IntegerField(default = 0)
    message         = models.TextField()
    content_type    = models.ForeignKey(ContentType)
    
    def __unicode__(self):
        return '%s: %s' % (self.relevant_date,self.content_type)
    
    class Meta:
        verbose_name_plural  = 'Logger'
        unique_together = (('relevant_date','content_type'),)
        get_latest_by   = "relevant_date"
        ordering        = ['-relevant_date']
        
        
    def save(self, *args, **kwargs):
        self.updated += 1
        super(Logger,self).save(*args, **kwargs)
            
        
        
    
        
    