
from qmpy.python.decorators import lazyattr
from base import *

__all__ = ['yc','convenienceComposite']


class yc(compositeDiscount):
    '''
    
    Yield curve composite rate
    '''
    scalar_rate_class = fixed_income_rate
    def __init__(self, *args, **kwargs):
        super(yc,self).__init__(*args, **kwargs)
        self.__support = None
        self.__cfs     = None
    
    def __get_support(self):
        return self.__support
    support = property(fget = __get_support)
    
    def _dft(self, T):
        '''
        Implementation of _dft,
        the discountcurve method
        '''
        # build if needed
        self.build()
        if self.__support:
            return self.__support[T]
        else:
            return self.badvalue
        
    def __buildCashFlow(self):
        '''
        Rebuild cash flow matrix
        '''
        rs    = self.inputrates
        cfmat = CashFlowMatrixRate()
        for r in rs:
            cf = r.cashflow
            # This will forse to get the rate value
            cf.rate.value
            cfmat.add(cf)
        return cfmat
    
    def rebuild_rate(self):
        self.__cfs = self.__buildCashFlow()
        self.refresh_rate()
        
    def refresh_rate(self):
        # Get cashflow for building
        cfmat = self.__cfs.cleaned(self)
        lhs,rhs,trhs = cfmat.refresh(self.dcf)
        if trhs == None:
            return
        else:
            sup = self.support
            if sup == None:
                sup = self.__initial(cfmat)
                self.__support = sup
            sup.build(lhs,rhs,trhs)
        
    def __initial(self, cfmat):
        '''
        Set the initial discount factor
        '''
        sup = qmlib.logsplinediscount()
        df  = self.T0
        T2  = 0.0
        sup.add(T2,df)
        cfmat = self.__cfs
        for kv in cfmat:
            dte = kv.key
            cfs = kv.value
            T1  = T2
            T2  = self.dcf(dte)
            tau = T2 - T1
            r   = cfs.rate.value
            df *= 1./(1.0 + 0.01*tau*r)
            sup.add(T2,df)
        return sup
    

class convenienceComposite(compositeDiscount):
    
    def __init__(self, support = None, yc = None, *args, **kwargs):
        super(convenienceComposite,self).__init__(*args, **kwargs)
        self.__yc = yc
        self.__support = support
        
    def __get_yc(self):
        return self.__yc
    yc = property(fget = __get_yc)
    