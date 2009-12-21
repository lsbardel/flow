
__all__ = ['Pricer','sensitivity','PricerNotAvailable']

from jflow.utils.observer import lazyobject


class PricerNotAvailable(Exception):
    "Pricer not available"
    def __init__(self, element):
        self.element  = str(element)
    
    def __str__(self):
        return 'Pricer not available for %s' % self.element
    
class DifferentDatesError(Exception):
    "Different dates"


class Pricer(lazyobject):
    '''
    Base class for pricing financial instrument
    '''
    def __init__(self, impl = None, *args, **kwargs):
        super(Pricer,self).__init__(*args, **kwargs)
        self.__dateobj = None
        self.__impl    = impl
        self.__rates   = {}
        
    def dateobj(self):
        return self.__dateobj
    
    def __get_date(self):
        if self.__dateobj:
            return self.__dateobj.date
        else:
            return None
    date = property(fget = __get_date)
    
    def __get_live(self):
        if self.__dateobj:
            return self.__dateobj.live
        else:
            return False
    live = property(fget = __get_live)
        
    def calculate(self, inst):
        return None
    
    def price(self, inst):
        '''
        Return the price for a given instrument
        '''
        # First check if the instrument code is a rate code as well
        ra = self.__rates.get(inst.code,None)
        if ra:
            return ra.value()
        else:
            return self.__impl.price(inst)
    
    def add(self, rte):
        from rate import rate
        if isinstance(rte,rate):
            if self.__dateobj == None:
                self.__dateobj = rte.dateobj()
            if self.__dateobj == rte.date.obj():
                if not self.__rates.has_key(rte.code()):
                    self.__rates[rte.code()] = rte
            else:
                raise DifferentDatesError
    
    
        
        
    
class sensitivity(object):
    
    def __init__(self):
        self.value  = 0
        self.deltas = {}
        self.gammas = {}
    
    
    
