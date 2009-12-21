

from base import finins, value_date_plugin

__all__ = ['equity']


class equity(finins, value_date_plugin):
    
    def __init__(self, value_date = None, *args, **kwargs):
        finins.__init__(self, *args, **kwargs)
        value_date_plugin.__init__(self, value_date = value_date, required = False)
    
    def pv01(self):
        m = self.multiplier()
        return 0.01*m*self.price()*self.size()
    
    def notional(self, size = 1):
        try:
            p = float(self.mktprice)
            return self.multiplier()*size*p
        except:
            return self.notavailable
    
    def nav(self, size):
        return self.notional(size)
        
        