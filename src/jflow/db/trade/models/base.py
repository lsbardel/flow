import datetime
from django.db import models
from django.utils.text import capfirst
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

current_app_label = 'trade'

ROUNDING   = 4
MAX_DIGITS = 18

#Positions status flags_________________________
POSITION_STATUS_DUMMY       = 0
POSITION_STATUS_SYNCRONIZED = 1
POSITION_STATUS_MANUAL      = 2
#_______________________________________________

NO_END_DATE    = datetime.date.max


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    import re
    rtx   = '-'
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return mark_safe(re.sub('[-\s]+', rtx, value))


class puser(models.Model):
    user = models.ForeignKey(User, unique=True, verbose_name = 'username')
    
    def fullname(self):
        u = self.user
        if u.first_name and u.last_name:
            return u'%s %s' % (capfirst(u.first_name),capfirst(u.last_name))
        else:
            return u.username
    
    def __unicode__(self):
        return u'%s' % self.user
    
    def is_active(self):
        return self.user.is_active
    is_active.boolean = True
    
    def is_staff(self):
        return self.user.is_staff
    is_staff.boolean = True
    
    def is_superuser(self):
        return self.user.is_superuser
    is_superuser.boolean = True
    
    def has_perm(self, perm):
        return self.user.has_perm(perm)
    
    class Meta:
        abstract = True


class TimeStamp(models.Model):
    last_modified     = models.DateTimeField(auto_now = True)
    created           = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True
        
        

class CodeDescriptionModel(models.Model):
    code = models.CharField(unique = True, max_length=32)
    name = models.CharField(max_length=62, blank = True)
    description = models.TextField(blank=True)
    
    def __unicode__(self):
        n = self.name
        if n:
            return u'%s - %s' % (self.code,n)
        else:
            return u'%s' % self.code
    
    class Meta:
        abstract = True
        
    def tojson(self):
        return {'code': self.code,
                'name': self.name,
                'description': self.description}
        
class CodeDescriptionModelTS(CodeDescriptionModel):
    last_modified     = models.DateTimeField(auto_now = True)
    created           = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True
    

