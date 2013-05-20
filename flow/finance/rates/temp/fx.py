

from qmpy.python.decorators import lazyattr
from base import *
from qmpy.finance.instruments import ccyrate

__all__ = ['crossfx']
    

class crossfx(compositeRate):
    '''
    Cross FX rate
    '''
    scalar_rate_class = ccyrate
    def __init__(self, *args, **kwargs):
        super(crossfx,self).__init__( *args, **kwargs)
        self.ycs = {}
    
    def swap(self, c1, c2):
        inv = False
        if c1.ccy.order > c2.ccy.order:
            ct = c1
            c1 = c2
            c2 = ct
            inv = True
        return inv,c1,c2
    
    @lazyattr
    def get_usd(self):
        u = self['USD']
        if u == None:
            raise KeyError, 'USD not available in currencies'
        return u
    
    def __codes(self, code):
        self.build()
        srte = trimCode(code)
        if len(srte) != 6:
            raise ValueError
        c1 = self[srte[:3]]
        c2 = self[srte[3:]]
        if c1 == None or c2 == None:
            raise ValueError
        return c1,c2
    
    def spot(self, c1, c2):
        if c1 == c2:
            return 1.0
        inverse, c1, c2 = self.swap(c1,c2)
        try:
            v1 = self.__value_ccy(c1)
            v2 = self.__value_ccy(c2)
        except:
            return self.badvalue
        try:
            v  = v1/v2
            if inverse:
                return 1./v
            else:
                return v
        except:
            return self.badvalue
        
    
    def get(self, code = None, fields = None):
        '''
        code must be a currency-pair string such as
            eurusd, gbpusd, usdchf etc...
        '''
        try:
            c1,c2 = self.__codes(code)
        except:
            return self.badvalue
        return self.spot(c1,c2)
    
    def __value_ccy(self, c1):
        v = c1.get()
        inv, c1, c2 = self.swap(c1, self.get_usd())
        if inv:
            return 1./v
        else:
            return v
        
    def fwd(self, code = None, valuedate = None, fields = None):
        try:
            c1,c2 = self.__codes(code)
        except:
            return self.badvalue
        v = self.spot(c1,c2)
        yc1 = self.__get_yc(c1)
        yc2 = self.__get_yc(c2)
        df1 = yc1.df(valuedate)
        df2 = yc2.df(valuedate)
        return v*df1/df2
        
    def __get_yc(self, c):
        from get import get_rate
        ycs = self.ycs
        yc  = ycs.get(c1,None)
        if yc == None:
            code = '%sYC' % c.code
            yc = get_rate(code)
            if yc:
                ycs[c1] = yc
        return yc
                
        