
from icash import *
from jflow.utils.observer import lazyvalue


class singlecash(icash):
    '''
    Simple cash flow.
    Date, currency and dummy implementation
    '''
    def __init__(self, date = None, dummy = False, ccy = None):
        self.__date  = date
        if self.__date == None:
            self.__date = dates.date.today()
        self.__ccy   = ccy
        self.__dummy = dummy
        
    def date(self):
        return self.__date
    
    def currency(self):
        return self.__ccy
    
    def isdummy(self):
        return self.__dummy


class fixcash(singlecash):
    '''
    Fixed cahs. Notional equal the cash ammount
    '''
    def __init__(self, value = 0., *args, **kwargs):
        super(fixcash,self).__init__(*args, **kwargs)
        self.__val = value
    
    def notional(self):
        return self.__val    


class lazycash(singlecash):
    
    def __init__(self, value = 5.0, *args, **kwargs):
        super(lazycash,self).__init__(*args, **kwargs)
        self.__val = value
    
    def __get_value(self):
        try:
            return self.__val.value
        except:
            return self.__val
    value = property(fget = __get_value)


class coupon(lazycash):
    
    def __init__(self, dcf = 1., notional = 1.0, *args, **kwargs):
        super(coupon,self).__init__(*args, **kwargs)
        self.__dcf = dcf
        self.__notional = notional
        
    def _descr(self):
        return '%s %s%s' % (self.__class__.__name__,self.value,'%')
        
    def dcf(self):
        return self.__dcf
    
    def notional(self):
        return self.__notional
    
    def cash(self):
        try:
            return 0.01*self.ndcf()*self.value
        except:
            return BADVALUE
    



