

from baseoper import tsoperator
from jflow.core.dates import converter
#import numpy as np
from jflow.core.timeseries import numericts, numerictsv, safe_unsigned

from simples import cctr, ptr

import math


def standardiseSeries(ts0, ldc, window, mult = 1.0):
    ns = numericts()
        
    for (dt, val), dc in zip(ts1.items(),ldc):
        ns[dt] = mult * val
        
        return ns
    

class RollingStatistics(tsoperator):
    
    class Meta:
        abstract = True
    
    def apply(self, ts, window = 20, **kwargs):
        window = safe_unsigned(window,20)
        ns = self.calculate(ts, window = window, **kwargs)
        return self.unwind.tsData(data = ns)
    
class RollingStatisticsN(tsoperator):
    
    def __init__(self, numseries = 2):
        self.numseries = numseries
        
    class Meta:
        abstract = True
    
    def apply(self, *tseries, **kwargs):
        n = len(tseries)
        if n != self.numseries:
            raise ValueError("Function requires %s timeseries as input. %s supplied" % (self.numseries,n))
        window = kwargs.pop('window',20)
        kwargs['window'] = safe_unsigned(window,20)
        ns = self.calculate(*tseries, **kwargs)
        return self.unwind.tsData(data = ns)
        
    
class avol(RollingStatistics):
    '''
    Calculate the realized annualized standard deviation (volatility) as percentage
    of the underlying value.
    '''
    fullname = 'annualized percentage volatility'
        
    def calculate(self, ts, window = 20, **kwargs):
        d = ts.econometric.slogdelta()
        return d.econometric.roll_vol(window)
    
class sharpe(RollingStatistics):
    '''
    Calculate the realized annualized Sharpe ratio
    '''
    name = 'Annualized Sharpe Ratio'
    
    class Meta:
        abstract = True
        
    def calculate(self, ts, window = 20, **kwargs):
        return ts.econometric.roll_sharpe(window)

class ar(RollingStatistics):
    '''
    Calculate the rolling realized autocorrelation coefficient
    '''
    fullname = 'Autocorrelation coefficient'
        
    def calculate(self, ts, window = 20, order = 1, **kwargs):
        order = safe_unsigned(order,1)
        d = ts.econometric.logdelta()
        return d.econometric.roll_ar(window,order)
    
    
class rcorr(RollingStatisticsN):
    
    '''
    Calculate the rolling percentage correlation of two timeseries.
    '''
    fullname = 'rolling correlation'
    
    def __init__(self):
        super(rcorr,self).__init__()
        
    def calculate(self, ts1, ts2, window = 20, **kwargs):
        tsv = ts1.econometric.slogdelta().tovector()
        tsv.addts(ts2.econometric.slogdelta())
        tsv.removemasked()
        correl = tsv.econometric.roll_correl(window)
        tsc = numericts()
        for k,v in correl.items():
            tsc[k] = v[0,1]
        return tsc

        
    