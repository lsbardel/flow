
from changes import rateChangeTraker

__all__ = ['Feed','InternalRateFeed']

class Feed(rateChangeTraker):
    
    def __init__(self, rate):
        rateChangeTraker.__init__(self)
        self.__rate = rate
        
    def __get_rate(self):
        return self.__rate
    rate = property(fget = __get_rate)
    
    def _value(self):
        return self.__rate.get()
    
    def __get_code(self):
        return self.__rate.code
    code = property(fget = __get_code)
    
    def __get_value(self):
        return self._value()
    value = property(fget = __get_value)
    
    def __str__(self):
        return '%s %s' % (self.__rate,self.value)
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self)
    
    def _available(self):
        return self.__rate._available()
    
    
class Feed2(Feed):
    def __init__(self, feed, obj = None):
        Feed.__init__(self, feed)
        self.obj = obj
        
    def _value(self):
        return self.rate.value
    
    
class InternalRateFeed(Feed2):
    '''
    A feed representing and internal rate. Used for fixed income feeds
    '''
    def __init__(self, feed, obj):
        Feed2.__init__(self, feed, obj)
        
    def _value(self):
        return self.obj.internalrate(self.rate.value)