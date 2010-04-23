from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

#from jflow.core import dates

from tagging.fields import TagField
from tagging.managers import ModelTaggedItemManager

#from jflow.djutils.fields import SlugCode

from base import *


__all__ = ['BaseModel',
           'DateRange',
           'Vendor',
           'DataId',
           'VendorId',
           'DataField',
           'MktData',
           'StringMktData',
           'MktDataCache',
           'VendorDataField',
           'get_vendor']


class MktDataCacheManager(models.Manager):
    
    def emptycache(self, dataid = None):
        if isinstance(dataid, DataId):
            qs = self.filter(vendor_id__dataid = dataid)
        else:
            qs = self.all() 
        qs.delete()


class BaseModel(models.Model):
    code           = models.CharField(max_length = 32, unique = True)
    name           = models.CharField(max_length = 64, blank  = True)
    description    = models.TextField(blank=True)
    
    def __unicode__(self):
        return u'%s' % self.code
    
    class Meta:
        abstract = True
  
    
class Vendor(BaseModel):
    '''
    Data Vendor
    '''    
    class Meta:
        app_label = current_app_label
        ordering  = ('code',)
    
    def summary(self):
        return mark_safe(self.description)
    
    def interface(self):
        module   = __import__(settings.VENDOR_MODULE,globals(),locals(),[''])
        return module.get_vendor(self.code)
    
    def save(self):
        c = self.code
        if LOWER_CASE_VENDORS:
            self.code = str(c).lower()
        else:
            self.code = str(c).upper()
        return super(Vendor,self).save()


class DataId(models.Model):
    '''
    Database ID
    '''
    #code           = SlugCode(max_length = 32, unique = True, upper = True, rtxchar = '_')
    code           = models.CharField(max_length = 32, unique = True)
    name           = models.CharField(max_length = 64, blank  = True)
    description    = models.TextField(blank=True)
    country        = models.CharField(max_length = 2, choices = geo.country_tuples())
    live           = models.BooleanField(default=True)
    default_vendor = models.ForeignKey(Vendor, blank = True, null = True)
    tags           = TagField('labels', blank = True, null = True,
                              help_text = _("Insert labels (keywords) separated by space"))
    
    objects        = ModelTaggedItemManager()

    #def save(self):
    #    code = self.code
    #    self.code = u'%s' % TrimCode(code)
    #    super(DataId,self).save()
        
    def get_country(self):
        return geo.country(self.country)
    
    def content_type(self):
        return ''
    
    def firm_code(self):
        return ''
    
    def curncy(self):
        return geo.countryccy(self.country)
    
    def defaultccy(self):
        return geo.countryccy(self.country)
        
    class Meta:
        app_label = current_app_label
        ordering  = ('code','country',)
        
    def __unicode__(self):
        if self.name:
            return u'%s - %s' % (self.code,self.name)
        else:
            return u'%s' % self.code
        
    def delete(self):
        ic = self.ic
        if ic:
            ic.delete()
        super(DataId,self).delete()
        
    def __get_ic(self):
        if not hasattr(self,'_lazy_ic'):
            ic = self.instrumentcode_set.all()
            N  = ic.count()
            if not N:
                self._layz_ic = None
            elif N == 1:
                self._layz_ic = ic[0]
            else:
                raise ValueError("Multiple instrument for data id %s" % self)
        return self._layz_ic
    ic = property(fget = __get_ic)
    
    def __get_dates_range(self):
        try:
            return self.daterange
        except:
            return None
    dates_range = property(fget = __get_dates_range)
        
    

class VendorId(models.Model):
    '''
    Vendor ticker for a given DataId
    For a DataId and a Vendor the entry should be unique.
    This is enforced in the Meta class.
    '''
    ticker = models.CharField(max_length=30)
    vendor = models.ForeignKey(Vendor)
    dataid = models.ForeignKey(DataId)
    #default_field = models.ForeignKey(DataField,blank=True,null=True)
    
    def __unicode__(self):
        return '%s' % self.ticker
    
    class Meta:
        app_label = current_app_label
        unique_together = (("dataid", "vendor"),)
        
    def dbcache(self, field):
        if not isinstance(field,DataField):
            field = DataField.objects.get(code = field)
        return MktDataCache.objects.filter(vendor_id = self, field = field)
        
        
class DataField(models.Model):
    '''
    Field of market data, could be ASK price, BID price, etc...
    '''
    code         = models.CharField(unique=True, max_length=32)
    description  = models.CharField(max_length=60, blank=True)
    format       = models.CharField(max_length=10, choices = field_type)
    
    class Meta:
        app_label = current_app_label
        
    def __unicode__(self):
        return '%s' % self.code
    
    
class MktDataBase(models.Model):
    vendor_id    = models.ForeignKey(VendorId)
    field        = models.ForeignKey(DataField)
    dt           = models.DateField(verbose_name='date')
    
    class Meta:
        abstract = True
        

class MktData(MktDataBase):
    mkt_value    = models.FloatField(default=0, blank=True, verbose_name='market value')
    
    class Meta:
        app_label = current_app_label
        verbose_name_plural = 'Market Data'
        get_latest_by   = 'dt'
        ordering        = ['dt']
        

class StringMktData(MktDataBase):
    mkt_value    = models.TextField(blank=True, verbose_name='market value')
    
    class Meta:
        app_label = current_app_label
        verbose_name_plural = 'Market Data'
        get_latest_by   = 'dt'
        ordering        = ['dt']


class MktDataCache(MktDataBase):
    mkt_value    = models.FloatField(default=0, blank=True, verbose_name='market value')
    
    objects = MktDataCacheManager()
    
    class Meta:
        app_label = current_app_label
        get_latest_by   = 'dt'
        ordering        = ['dt']
        

class DateRange(models.Model):
    start       = models.DateField(null=True,blank=True)
    end         = models.DateField(null=True,blank=True)
    dates_range = models.OneToOneField(DataId)
    
    def __unicode__(self):
        if self.start and self.end:
            return u'from %s to %s' % (self.start,self.end)
        elif self.start:
            return u'from %s' % self.start
        elif self.end:
            return u'to %s' % self.end
        else:
            return u''
        
    class Meta:
        app_label = current_app_label
        

class VendorDataField(models.Model):
    vendor = models.ForeignKey(Vendor)
    field  = models.ForeignKey(DataField)
    code   = models.CharField(max_length = 200, blank = False)
    
    def __unicode__(self):
        return '%s: %s (%s)' % (self.code,self.field,self.vendor)
    
    class Meta:
        unique_together = (('vendor','field'),)
        app_label = current_app_label
        
        
        
def get_vendor(code):
    if settings.LOWER_CASE_VENDORS:
        code = str(code).lower()
    else:
        code = str(code).upper()
    try:
        return Vendor.objects.get(code = code)
    except:
        return None