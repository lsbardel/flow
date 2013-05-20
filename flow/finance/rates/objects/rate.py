from jflow.conf import settings
from jflow.core import dates

from lazy import lazyrate

__all__ = ['Rate','rdate']


class Rate(object):
    '''
    Interface class for financial rates.
    '''
    def __init__(self, holder):
        self.__holder = holder
        
    def __get_holder(self):
        return self.__holder
    '''
    This is the ratehistory holder.
    The object which hold the rate (see jflow.core.rates.handler.history)
    '''
    holder = property(fget = __get_holder)
    
    def __get_factory(self):
        return self.holder.factory
    factory = property(fget = __get_factory)
    
    def __get_cache(self):
        return self.__holder.cache
    cache = property(fget = __get_cache)
        
    def __unicode__(self):
        return u'%s' % self
        
    def __str__(self):
        return '%s %s' % (self._code(),self.dateobj())
    
    def __repr__(self):
        return '%s - %s' % (self.__class__.__name__,self)
    
    def dateobj(self):
        '''
        Needs to return an object with the following properties
          live  - boolean
          date  - datetime object
        '''
        pass
    
    def __get_date(self):
        return self.dateobj().date
    date = property(fget = __get_date)
    
    def samedateas(self, r):
        return self.dateobj() == r.dateobj()
    
    def _code(self):
        return self.factory.code()
    
    def __get_code(self):
        return self._code()
    code = property(fget = __get_code)
    
    def __get_live(self):
        return self.dateobj().live
    live = property(fget = __get_live)
    
    def __get_badvalue(self):
        return settings.BADVALUE
    badvalue = property(fget = __get_badvalue)
    
    def get(self, *args, **kwargs):
        raise TypeError, 'Value not available for %s' % self
    
    def clear(self):
        pass
    
    def clearlive(self, live_key):
        pass
    
    def pingrate(self):
        raise NotImplementedError


class rdate(Rate,lazyrate):
    '''
    Implements rate 'date' method
    '''
    def __init__(self, holder = None, dte = None):
        Rate.__init__(self, holder)
        lazyrate.__init__(self)
        self.__date = dates.get_livedate(dte)
            
    def dateobj(self):
        return self.__date
    
    def pingrate(self):
        return self.get()
    


    