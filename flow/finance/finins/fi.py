
from base import *


__all__ = ['immIrFuture',
           'bondfuture',
           'BulletBond']
    

class immIrFuture(IrFuture):
    
    def __init__(self, *args, **kwargs):
        super(immIrFuture,self).__init__(*args, **kwargs)
    
    def _calc_cash_start_date(self):
        d1 = self.end_date()
        return dates.nextimmdate(d1,'')
    
    def _calc_cash_end_date(self):
        d1 = self.end_date()
        return dates.nextimmdate(d1,self.cash_tenure)
    

class billfuture(IrFuture):
    
    def __init__(self, *args, **kwargs):
        super(aud90daybankbill,self).__init__(*args, **kwargs)
        
    def _yearfraction(self):
        return 90.0/365.0
    
    def pv01(self):
        tau,df,p  = self.taudfp()
        return 0.0001*p*tau/df
    
    def notional(self):
        return 1000000*self.size
    
    def pv(self):
        tau,df,p  = self.taudfp()
        return p
        
    def taudfp(self):
        tau = self.year_fraction
        rate = 0
        df   = (1. + 0.01*tau*rate)
        p    = self.notional()/df
        return tau,df,p


class bondfuture(FiFuture):
    
    def __init__(self, *args, **kwargs):
        super(bondfuture,self).__init__(*args, **kwargs)
        
        

class BulletBond(bond, value_date_plugin):
    
    def __init__(self, value_date = None, *args, **kwargs):
        value_date_plugin.__init__(self, value_date = value_date, required = False)
        cappend = self.value_date_string
        bond.__init__(self, append_to_code = cappend, *args, **kwargs)
        
    def notional(self, size = 1):
        try:
            p = float(self.mktprice)
            return self.multiplier()*size*p
        except:
            return self.notavailable
    
    def nav(self, size):
        return self.notional(size)
        
    
        
        
        
    
        