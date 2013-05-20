
from cashflowrate import *


class cash_flow_interface(object):
    '''
    Interface for a cash-flow instrument
    '''
    def _cashflow(self, dte = None, notional = None):
        pass
        
    def cashflow(self, dte = None, notional = None):
        return self._cashflow(dte = dte, notional = notional)
    
    def simplecashflow(self, dte = None):
        return self.cashflow(dte = dte, notional = 100.0)
    
    def plot_simplecashflow(self, dte = None):
        pass
    
    def curve_priority(self):
        return 1



class cashinst(finins, cash_flow_interface):
    '''
    Simple cash instrument
    '''
    def __init__(self, settle_date = None, *args, **kwargs):
        super(cash,self).__init__(*args, **kwargs)
        self.dte      = settle_date
        
    def end_date(self):
        return self.dte
    
    def cashflow(self, dte = None):
        cf = CashFlow()
        if dte <= self.end_date():
            fc = fixcash(value = self.notional, ccy = self.ccy())
            cf.add(self.end_date(),fc)
        return cf
    
    def nav(self, size = 1):
        return self.notional(size)
    
    
class CashInst(finins):
    '''
    Simple cash instrument
    '''
    def __init__(self, *args, **kwargs):
        super(CashInst,self).__init__(*args, **kwargs)
        
    def mktvalue(self):
        return self.notional()
    
    def nav(self, size = 1):
        return self.notional(size)
        