
from jflow.db import geo

from base import *
from instrument import NoDataInstrumentBase
import factory as FACTORY

cash_types = (
              (1,'Principal'),
              (2,'Income'),
              (3,'Margin'),
              (4,'Call Account'),
              )

cash_type_dict = dict_from_choices(cash_types)

def cash_code_from_type(typ):
    v = cash_type_dict.get(typ,'   ')[:3]
    return v.upper()
    
              

class Cash(NoDataInstrumentBase):
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    type   = models.IntegerField(choices = cash_types)
    
    def has_firm_code(self):
        return False
    
    def name(self):
        return self.description()
    
    def description(self):
        return 'cash %s' % cash_type_dict.get(self.type,'').lower()
    
    class Meta:
        unique_together = (('curncy','type'),)
        app_label  = current_app_label
        
    def ccy(self):
        return self.curncy
    
    def iscash(self):
        return True
        
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, **kwargs)
    
class FwdCash(NoDataInstrumentBase):
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    value_date = models.DateField()
    
    class Meta:
        verbose_name = 'Forward Cash'
        verbose_name_plural = 'Forward Cash'
        app_label  = current_app_label
        
    def description(self):
        return 'Forward %s cash %s' % (self.curncy, self.value_date)
    
    def name(self):
        return self.description()
    
    def ccy(self):
        return self.curncy
    
    def iscash(self):
        return True
    
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, value_date = self.value_date, **kwargs)
    

class Depo(NoDataInstrumentBase):
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    value_date = models.DateField()
    
    class Meta:
        app_label  = current_app_label
        
    def description(self):
        return '%s Deposit: expiry %s' % (self.curncy, self.value_date)
    
    def name(self):
        return self.description()
    
    def ccy(self):
        return self.curncy
    
    def iscash(self):
        return True
    
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, value_date = self.value_date, **kwargs)
        
    
class Forex(NoDataInstrumentBase):
    ccy_pair   = models.CharField(max_length=6,choices=geo.currency_pair_tuples())
    value_date = models.DateField()
    
    def iscash(self):
        return True
    
    def has_firm_code(self):
        return False
    
    class Meta:
        app_label  = current_app_label
        unique_together = (('ccy_pair','value_date'),)
        
    def make_position(self, **kwargs):
        return FACTORY.forex(inst = self, **kwargs)
    
    
class CashMisc(NoDataInstrumentBase):
    name           = models.CharField(max_length = 64, blank  = True)
    description    = models.TextField(blank=True)
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    
    def iscash(self):
        return True
    
    def ccy(self):
        return self.curncy

    def make_position(self, **kwargs):
        return None
    
    class Meta:
        app_label  = current_app_label