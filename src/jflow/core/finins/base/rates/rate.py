
from jflow.conf import settings
from jflow.core import dates

__all__ = ['Rate','rdate']


class Rate(object):
    '''
    Interface class for financial rates.
    '''
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
    
    def holder(self):
        pass
    
    def __get_date(self):
        return self.dateobj().date
    date = property(fget = __get_date)
    
    def __get_livehandle(self):
        r = self.holder()
        if not r:
            return None
        try:
            return r.liveHandle
        except:
            return None
    liveHandle = property(fget = __get_livehandle)
    
    def samedateas(self, r):
        return self.dateobj() == r.dateobj()
    
    def _code(self):
        pass
    
    def __get_code(self):
        return self._code()
    code = property(fget = __get_code)
    
    def __get_live(self):
        return self.dateobj().live
    live = property(fget = __get_live)
    
    def composite(self):
        return False
    
    def __get_badvalue(self):
        return settings.BADVALUE
    badvalue = property(fget = __get_badvalue)
    
    def get(self, *args, **kwargs):
        raise TypeError, 'Value not available for %s' % self
    
    
class rdate(Rate):
    '''
    Implements rate 'date' method
    '''
    def __init__(self, dte = None, holder = None):
        ld = dates.livedate
        self.__holder = holder
        if dte == None:
            self.__date = ld()
        elif isinstance(dte,ld):
            self.__date = dte
        else:
            self.__date = ld(dte = dte)
            
    def holder(self):
        return self.__holder
            
    def dateobj(self):
        return self.__date


    