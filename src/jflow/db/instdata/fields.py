import re
import unicodedata

from django.db import models
from django.db.models.fields import NOT_PROVIDED
from django.conf import settings


def slugify(value, rtx = '_'):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    return re.sub('[-\s]+', rtx, value)

class SlugCode(models.CharField):
    
    def __init__(self, rtxchar='_', lower=False, upper = True, **kwargs):
        self.rtxchar = u'%s' % rtxchar
        self.lower   = lower
        self.upper   = upper
        super(SlugCode,self).__init__(**kwargs)
        
    def trim(self, value):
        value = slugify(u'%s'%value, rtx = self.rtxchar)
        if self.lower:
            value = value.lower()
        elif self.upper:
            value = value.upper()
        return value
        
    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        value = self.trim(value)
        setattr(model_instance, self.attname, value)
        return value

if 'south' in settings.INSTALLED_APPS:
    rules = [
        (
        (SlugCode, ),
            [],
        {
            "null": ["null", {"default": False}],
            "blank": ["blank", {"default": False, "ignore_if":"primary_key"}],
            "primary_key": ["primary_key", {"default": False}],
            "max_length": ["max_length", {"default": None}],
            "unique": ["_unique", {"default": False}],
            "db_index": ["db_index", {"default": False}],
            "default": ["default", {"default": NOT_PROVIDED}],
            "db_column": ["db_column", {"default": None}],
            "db_tablespace": ["db_tablespace", {"default": settings.DEFAULT_INDEX_TABLESPACE}],
        },
            ),
        ]
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules, ["^jflow\.db\.instdata"])



class LazyManyToOneRel(models.ManyToOneRel):
    '''
    A ManyToOneRel class with lazy limit_choices_to
    Useful for ContentType filtering 
    '''
    def __init__(self, to, field_name, related_name=None,
            limit_choices_to=None, lookup_overrides=None, parent_link=False):
        try:
            to._meta
        except AttributeError: # to._meta doesn't exist, so it must be RECURSIVE_RELATIONSHIP_CONSTANT
            assert isinstance(to, basestring), "'to' must be either a model, a model name or the string %r" % RECURSIVE_RELATIONSHIP_CONSTANT
        self.to, self.field_name = to, field_name
        self.related_name = related_name
        self.__limit_choices_to = limit_choices_to
        self.__lct_val   = None
        self.lookup_overrides = lookup_overrides or {}
        self.multiple = True
        self.parent_link = parent_link
        
    @property
    def limit_choices_to(self):
        if self.__lct_val is None:
            c = self.__limit_choices_to
            if callable(c):
                c = c()
            self.__lct_val = c or {}
        return self.__lct_val


class LazyForeignKey(models.ForeignKey):
    
    def __init__(self, *args, **kwargs):
        kwargs['rel_class'] = LazyManyToOneRel
        super(LazyForeignKey,self).__init__(*args, **kwargs)


import math

from jflow.core.field import fieldproxy

def calc3vol(ds1,ds2,ds3):
    dsa = (ds1+ds2+ds3)/3.0
    return (ds1*ds1+ds2*ds2+ds3*ds3)/3.0 - dsa*dsa


class premium(fieldproxy):
    def __init__(self,code = 'PREM'):
        super(premium,self).__init__(code,'LAST_PRICE','NAV')
        
    def value(self, rate):
        s1 = rate.get('LAST_PRICE')
        s2 = rate.get('NAV')
        if s1 and s2:
            return 100*(s1 - s2)/s2
        else:
            return None

class intravol(fieldproxy):
    
    def __init__(self,code = 'INTRAVOL'):
        super(intravol,self).__init__(code,'LAST_PRICE','OPEN_PRICE','LOW_PRICE','HIGH_PRICE')
    
    def value(self, rate):
        s1 = rate.get('OPEN_PRICE')
        s2 = rate.get('LOW_PRICE')
        s3 = rate.get('HIGH_PRICE')
        s4 = rate.get('LAST_PRICE')
        if s1 and s2 and s3 and s4:
            av = (s1+s2+s3+s4)/4.0
            ds1 = s2-s1
            ds2 = s2-s3
            ds3 = s3-s4
            v1  = calc3vol(s2-s1,s3-s2,s4-s3)
            v2  = calc3vol(s3-s1,s2-s3,s4-s2)
            return 100*math.sqrt(252*(v1+v2)/2.0)/av
        else:
            return None