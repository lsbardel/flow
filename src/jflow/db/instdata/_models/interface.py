from django.db import models
from django.utils.encoding import force_unicode
from django.utils.datastructures import SortedDict

from jflow.db.instdata.lineardecomp import LinearDecomp

from base import *

__all__ = ['InstrumentInterface',
           'attribute_wrapper']


class InstrumentInterface(models.Model):
    InstrumentFactory = None
    has_data_id       = True
    
    class Meta:
        abstract = True
    '''
    Interface class for all instrument models
    '''
    def data_link(self):
        return False
    
    def tags(self):
        return ''
    
    def get_multiplier(self):
        return 1.0
    
    def description(self):
        return ''
    
    def name(self):
        return None
    
    def instype(self):
        '''
        Instrument type
        '''
        opt = self._meta
        return force_unicode(opt.verbose_name)
    
    def asset_class(self):
        try:
            return self.type().asset_class
        except:
            return None
        
    def country(self):
        return None
    
    def ccy(self):
        return None
    ccy.short_description = 'currency'
    
    def trading_centre(self):
        c = self.ccy()
        if c:
            return c.trading_centre
        else:
            return None
    
    def end_date(self):
        return None
    
    def live(self):
        return True
    
    def Contract(self):
        return None
    
    def isotc(self):
        return True
    
    def iscash(self):
        return False
    
    def tonotional(self, size):
        return size
    
    def GetDateRange(self):
        return None
    
    def get_data_id(self):
        return None
    
    def need_value_date(self):
        return False
    
    def sett_delay(self):
        return 0
    
    def get_underlying(self):
        return None
    
    def instrumentsAtValueDate(self):
        return []
    
    def PriceAtSettlement(self, size, value, i):
        return value
    
    def SizeAtSettlement(self, size, value, i):
        return size
    
    def make_position(self, **kwargs):
        pass
    
    def calculate_value_date(self, dte):
        from qmpy.finance import dates
        delay = inst.sett_delay()
        tc    = inst.trading_centre()
        tcs   = ''
        #if tc:
        #    tcs = tc.code
        return dates.nextbizday(date = dte, numdays = delay, tcs = tcs)
    
    def infodict(self):
        ic = self.code
        rval = SortedDict()
        rval['code']= str(self.code)
        if ic.firm_code:
            rval[settings.FIRM_CODE_NAME] = ic.firm_code 
        rval['name']= self.name()
        rval['CCY'] = self.ccy()
        rval['country'] = self.country()
        rval['description'] = self.description()
        rval['tags'] = self.tags()
        c = self.lineardecomp()
        if c.data:
            rval['composition'] = c.data
        return rval
    
    def lineardecomp(self):
        from decomp import InstDecomp
        dc = InstDecomp.objects.forobject(self.code)
        return LinearDecomp(dc)
    
    def tojson(self):
        return dict(self.infodict())
    


class attribute_wrapper(object):
    
    def __init__(self,obj,verbose_name):
        self.short_description = verbose_name
        self.obj = obj
    
    def __str__(self):
        return str(self.obj)
    
    def __unicode__(self):
        return u'%s' % str(self)
    
    def __repr__(self):
        return self.obj.__repr__()