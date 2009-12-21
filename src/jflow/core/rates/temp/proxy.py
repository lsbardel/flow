
from base import *


__all__ = ['proxyrateConst','compositeProxy','ccypairProxy']



class proxyrateConst(proxyrate):
    
    def __init__(self, value = 1.0):
        self.__value = 1.0
        
    def _get_value_at_date(self, dateobj):
        return {'LAST_PRICE': self.__value}
    

class compositeProxy(proxyrate):
    
    def __init__(self, factory = None):
        self.__factory = factory
        
    def get_composite_rate(self, dateobj):
        if dateobj.live:
            return self.__factory.get_or_make(None)
        else:
            return self.__factory.get_or_make(dateobj.date)
        
    def _get_value_at_date(self, dateobj):
        cr = self.get_composite_rate(dateobj)
        if cr == None:
            return None
        else:
            v = cr.get(str(self))
            return {'LAST_PRICE': v}
    

class ccypairProxy(compositeProxy):
    
    def __init__(self, c1, c2, factory):
        compositeProxy.__init__(self,factory=factory)
        self.c1 = c1
        self.c2 = c2
        
    def __str__(self):
        return '%s%s' % (self.c1,self.c2)
    