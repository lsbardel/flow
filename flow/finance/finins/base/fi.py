#
# FixedIncome base classes
#
from jflow.utils.decorators import lazyattr

from cash import *
from rates import fixed_income_rate

__all__ = ['cashinst','FiInstrument','FiFuture','IrFuture','bond']


class FiInstrument(finins, cash_flow_interface):
    '''
    Fixed Income instrument
    '''
    def __init__(self, *args, **kwargs):
        finins.__init__(self, *args, **kwargs)
        
    def rate_klass(self):
        return fixed_income_rate
    
    def internalrate(self, v):
        try:
            v = float(v)
        except:
            return v
        return self._internalrate(v)
    
    def _internalrate(self, v):
        return v
        

class FiFuture(FiInstrument, future_instrument):
    '''
    Fixed Income base future class
    '''
    def __init__(self, *args, **kwargs):
        FiInstrument.__init__(self, *args, **kwargs)
        

class bond(FiInstrument):
    
    def __init__(self, *args, **kwargs):
        super(bond,self).__init__(*args, **kwargs)
        



class IrFuture(FiFuture):
    '''
    Base class for interest rate futures
    '''
    def __init__(self, period = '3M', dc = None, delay = 0, *args, **kwargs):
        '''
        Tenure is a string indicating the tenure
        of the underlying deposit rate.
        '''
        self.cash_tenure      = dates.get_period(str(period),'3M')
        self.__dc             = dates.get_daycount(dc)
        self.__delay          = delay
        super(IrFuture,self).__init__(*args, **kwargs)
        ed = self.end_date()
        self.__cash_start_date = self._calc_cash_start_date()
        self.__cash_end_date   = self._calc_cash_end_date()
        self.__dcf             = self._calculate_dcf()
        
    def _yearfraction(self):
        return self.cash_tenure.year_fraction
    
    def pv01(self):
        return 0.01*self.dbinstrument.tonotional(self.size)
    
    def notional(self):
        return 10000*self.pv01()/self.year_fraction
    
    def pv(self):
        pass
        
    def __get_dc(self):
        return self.__dc
    dc = property(fget = __get_dc)
    
    def __get_dcf(self):
        return self.__dcf
    dcf = property(fget = __get_dcf)
    
    def __get_year_fraction(self):
        return self._yearfraction()
    year_fraction = property(fget = __get_year_fraction)

    def __get_cash_start_date(self):
        return self.__cash_start_date
    cash_start_date = property(fget = __get_cash_start_date)
    
    def __get_cash_end_date(self):
        return self.__cash_end_date
    cash_end_date = property(fget = __get_cash_end_date)
    
    def _calc_cash_start_date(self):
        pass
    
    def _calc_cash_end_date(self):
        pass
        
    def _calculate_dcf(self):
        return self.dc.dcf(self.cash_start_date,self.cash_end_date)
    
    def _cashflow(self, dte = None, notional = None):
        rate = InternalRateFeed(self.rateobj, self)
        cf   = CashFlowRate(priority = self.curve_priority(), rate = rate)
        no   = notional
        if no == None:
            no = self.notional()
        sd   = self.cash_start_date
        ed   = self.cash_end_date
        c    = coupon(date = ed, dummy=True, value = rate, dcf = self.dcf, notional = no)
        cf.add(fixcash(date = sd, dummy=True, value = -no))
        cf.add(fixcash(date = ed, dummy=True, value =  no))
        cf.add(c)
        return cf
    
    @lazyattr
    def __get_coupon(self):
        c = coupon(dcf = self.dcf, notional = self.notional())
    rate = property(fget = __get_coupon)
    
    def _internalrate(self, v):
        return 100.0 - v
