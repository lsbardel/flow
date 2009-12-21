from jflow.core.dates import get_livedate
from jflow.utils.decorators import threadSafe

from lazy import lazyrate
from rate import Rate

__all__ = ['composite', 'compositeRate', 'compositeDiscount']


class composite(lazyrate):
    '''
    This class provides the functionalities for composite rates.
    This is not a rate interface but a functional class.
    This class should be derived by a composite rate class
    '''
    def __init__(self, *args, **kwargs):
        super(composite,self).__init__(*args, **kwargs)
        self.__input_rates     = {}
        self.__rates           = {}
        self.__rateadded       = False
        self.__needupdate      = False
        
    def __len__(self):
        return len(self.__rates)
        
    def add(self, r):
        '''
        Add a rate to the composite object
        r must be a scalar_rate_class instance
        '''
        if self.check_rate(r):
            if r.samedateas(self):
                k = r.code
                d = self.__input_rates
                if not d.has_key(k):
                    d[k] = r
                    self.__rateadded  = True
                    r.attach(self)
                    
    def update_me(self, args = None):
        self.build()
        return self
    
    def check_rate(self, r):
        return isinstance(r,Rate)
   
    def __getitem__(self, code):
        return self.__rates.get(trimCode(code),None)
    
    def __get_rates(self):
        return self.__rates
    rates = property(fget = __get_rates)
    
    def __get_input_rates(self):
        return self.__input_rates
    inputrates = property(fget = __get_input_rates)
    
    def __get_need_update(self):
        return self.__needupdate
    needupdate = property(fget = __get_need_update)
    
    def __get_rate_added(self):
        return self.__rateadded
    rateadded = property(fget = __get_rate_added)
    
    def build(self):
        if self.__rateadded:
            self.rebuild_rate()
            self.__rateadded = False
        else:
            self.refresh_rate()
        
    def rebuild_rate(self):
        self.__rates = self.__input_rates

    def refresh_rate(self):
        pass
    


class compositeRate(Rate, composite):
    '''
    Base class for composite Rates
    '''
    def __init__(self, holder = None, dte = None, *args, **kwargs):
        Rate.__init__(self,holder)
        composite.__init__(self)
        self.__date = get_livedate(dte)
        
    def dateobj(self):
        return self.__date
    
    def pingrate(self):
        for r in self.inputrates.values():
            r.pingrate()
        self.build()
    
        
    

