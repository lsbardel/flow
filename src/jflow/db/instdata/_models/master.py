import datetime

from django.db import models

from jflow.db.utils import django_choices
from jflow.db import geo
from jflow.core import dayCount_choices

from base import *

__all__ = ['Exchange',
           'SecurityClass',
           'FutureContract',
           'IndustryCode',
           'CouponType',
           'BondMaturityType',
           'BondClass',
           'CollateralType']


class Exchange(models.Model):
    code = models.CharField(unique=True, max_length=12)
    name = models.CharField(max_length=50, blank=True)
    
    class Meta:
        app_label = current_app_label
        ordering = ('code',)
        
    def __unicode__(self):
        return u'%s - %s' % (self.code,self.name)    


class SecurityClass(models.Model):
    '''
    Abstract model for security classes
    '''
    code             = models.CharField(unique=True, max_length=12)
    curncy           = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    country          = models.CharField(max_length = 2, choices = geo.country_tuples())
    exchange         = models.ForeignKey(Exchange,null=True,blank=True)
    description      = models.CharField(max_length=60,blank=True)
    price_type       = models.CharField(max_length=10,choices=Future_Price_Types,blank=True)
    index            = models.ForeignKey('DataId',null=True,blank=True)
    #long_description = models.CharField(max_length=100,blank=True)
    
    def __unicode__(self):
        return u'%s - %s' % (self.code,self.description)
    
    class Meta:
        abstract = True
   
    

class FutureContract(models.Model):
    code           = models.CharField(unique=True, max_length=12)
    curncy         = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    country        = models.CharField(max_length = 2, choices = geo.country_tuples())
    exchange       = models.ForeignKey(Exchange,null=True,blank=True)
    description    = models.CharField(max_length=60,blank=True)
    price_type     = models.CharField(max_length=10,choices=Future_Price_Types,blank=True)
    index          = models.ForeignKey('DataId',null=True,blank=True)
    expiry_months  = models.CharField(max_length=24,blank=True)
    trading_unit   = models.CharField(max_length=32,blank=True)
    tick_size      = models.FloatField()
    tick_value     = models.FloatField()
    ticket_cost    = models.FloatField(default=0.0)
    term_structure = models.IntegerField(default = 0)
    type           = models.CharField(max_length=12, choices = future_type_choice)
    
    class Meta:
        app_label = current_app_label
        ordering = ('type','code',)
        
    def __unicode__(self):
        return u'%s - %s' % (self.code,self.description)
        
    def tonotional(self, size):
        return self.tick_value*size/self.tick_size
        
    def blbcom(self):
        ac = str(self.asset_class.code)
        if ac == 'EQ':
            return 'Index'
        else:
            return 'Comdty'

  
class BondMaturityType(models.Model):
    code = models.CharField(unique=True, max_length=32)
    description = models.CharField(blank=True,max_length = 255)
    
    class Meta:
        app_label = current_app_label
        
    def __unicode__(self):
        return u'%s' % self.code
    

class CouponType(models.Model):
    code            = models.CharField(choices = Coupon_type, max_length=20)
    month_frequency = models.IntegerField(default=12)
    day_count       = models.CharField(choices = dayCount_choices, max_length=20)
    
    class Meta:
        abstract  = True
        app_label = current_app_label
        unique_together = (("code", "month_frequency", "day_count"),)
        ordering = ('code','month_frequency')
        
    def __unicode__(self):
        return self.description()
    
    def description(self):
        return u'%s-%s-%s' % (self.code,self.frequency(),self.day_count)
    
    def frequency(self):
        mf = self.month_frequency
        if mf == 6:
            return 'SemiAnnual'
        elif mf == 12:
            return 'Annual'
        elif mf == 3:
            return 'Quarterly'
        else:
            return 'Every %s months' % mf
    

class BondClass(models.Model):
    code             = models.CharField(unique=True,max_length=12)
    curncy           = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    country          = models.CharField(max_length = 2, choices = geo.country_tuples())
    #exchange         = models.ForeignKey(Exchange,null=True,blank=True)
    description      = models.CharField(max_length=60,blank=True)
    price_type       = models.CharField(max_length=10,choices=Future_Price_Types,blank=True)
    index            = models.ForeignKey('DataId',null=True,blank=True)
    #coupon_type      = models.ForeignKey(CouponType)
    #settlement_delay = models.SmallIntegerField(default = 3)
    sovereign        = models.BooleanField(default=False)
    #callable         = models.BooleanField(default=False)
    #putable          = models.BooleanField(default=False)
    convertible      = models.BooleanField(default=False)
    bondcode         = models.CharField(null=True,max_length=12)
    
    class Meta:
        app_label = current_app_label
        verbose_name_plural = 'Bond Classes'
        ordering = ('code',)
        
    def fulldescription(self):
        return '%s bond. %s' % (self.description,
                                self.coupon_type)
        
    def __unicode__(self):
        return self.code
        
    def settlement(self):
        return 'T + %s' % self.settlement_delay
    
    def issuer(self, dt = None):
        dt = dt or datetime.date.today()
        iss = self.issuers.filter(dt__lte = dt)
        if iss:
            return iss.latest
        else:
            return None
            
class CollateralType(models.Model):
    name = models.CharField(max_length=60,unique=True)
    order = models.PositiveIntegerField(default = 1)
    
    class Meta:
        app_label = current_app_label
        ordering  = ('order',)
        
    def __unicode__(self):
        return self.name


class IndustryCode(models.Model):
    id           = models.IntegerField(primary_key=True)
    code         = models.CharField(unique=True, max_length=64)
    description  = models.TextField(blank=True)
    parent       = models.ForeignKey('self', null = True, blank = True)
    
    class Meta:
        app_label = current_app_label
        
    def __unicode__(self):
        return u'%s - %s' % (self.id, self.code)