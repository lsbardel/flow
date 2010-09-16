

from baseoper import tsoperator
from jflow.core.dates import converter
import numpy as np
import rpy2.robjects.numpy2ri
from loadr import robject

from jflow.core.timeseries import numericts, numerictsv, safe_unsigned

from simples import cctr, ptr

import math


def standardiseSeries(ts0, ldc, window, mult = 1.0):
    ns = numericts()
        
    for (dt, val), dc in zip(ts1.items(),ldc):
        ns[dt] = mult * val
        
        return ns        

    
class rSingleTS(tsoperator):
    '''Generic class for performing rolling functions on a single timeseries using R functions'''    
    
    r = robject()
    
    def __init__(self,rfunc):                      
        self.rApplyFunc = self.r['rollapply']
        self.rFunc = self.r[rfunc]
        
    class Meta:
        abstract = True
    
    def tsToZoo(self,ts):
        '''
        Takes a timeseries object and returns a zoo object
        '''
        adt = np.empty((len(ts),1),np.long)
        ats = np.empty((len(ts),1)) 
        i = 0
        for k , v  in ts.items():
            adt[i] = converter.date2yyyymmdd(k)
            ats[i] = v
            i = i + 1
        
        r_zoo = self.r['zoo']
        zooTs = r_zoo(ats,adt)
        
        return zooTs
    
    def zooToTs(self,zooTs):
        '''Takes a zoo object and returns a timeseries object'''
        ns = self.newts()
        
        r_index = self.r['index']
        
        core_data = self.r['coredata'](zooTs)
        dts = r_index(zooTs)
        
        for k,v in zip(dts,core_data):
            kDt = converter.yyyymmdd2date(k)
            ns[kDt] = v
            
        return ns
    
    def calculate(self, ts, window = 2, align = "center"):
        zoo_ts = self.tsToZoo(ts) #Zoo object matching the dataseries
        
        _result = self.rApplyFunc(zoo_ts,window,self.rFunc,align = align)
        
        return self.zooToTs(_result)
        
    def apply(self, ts, window = 20, align = "right"):
        try:
            window = int(window)
            window = max(1,window)
        except:
            window = 20
        ns = self.calculate(ts, window = window, align = align)        
        
        return self.unwind.tsData(data = ns)
    
         
class ma(rSingleTS):
    '''
    Returns the rolling mean (moving average) for a time series.
    '''
    def __init__(self):
        super(ma,self).__init__('mean')


class std_base(rSingleTS):
    
    def __init__(self):
        super(std_base,self).__init__('sd')
        
    class Meta:
        abstract = True
        
        
        
class std(std_base):
    '''
    Standard deviation
    '''
    def __init__(self):
        super(std,self).__init__('sd')
        
    def calculate(self, ts, window = 20, standard = 'a', align = 'right', mult = 1.0):
        if type == 'r':
            ns = delta(ts)
        elif type == 'lr':
            mult = 100.0
            ns = logdelta(ts) 
        else:
            ns = ts
            raise FunctionArgumentError('std','Did not recognise %s type of return, only "lr" and "r" accepted' % r )
        
        stdev_ts = super(std,self).calculate(ts=ns,window=window, align=align)
        
        if standard == 'a':
            return standardiseSeries(ts0 = ns,ts1 = stdev_ts, window=window, mult = mult)
        return stdev_ts
        
        
    def apply(self, ts, window = 20, type = None, standard = 'a', align = 'right'):
        '''
            type 'r' or 'lr'
        '''
        ns = self.calculate(ts, window = window, type = type, standard = standard, align = align)        
        
        return self.unwind.tsData(data = ns)
    
    
class avol(RollingStatistics):
    '''
    Calculate the realized annualized standard deviation (volatility) as percentage
    of the underlying value.
    '''
    name = 'Annualized percentage volatility'
        
    def calculate(self, ts, window = 20, **kwargs):
        d = ts.econometric.slogdelta()
        return d.econometric.roll_vol(window)
    
class sharpe(RollingStatistics):
    '''
    Calculate the realized annualized Sharpe ratio
    '''
    name = 'Annualized Sharpe Ratio'
        
    def calculate(self, ts, window = 20, **kwargs):
        return ts.econometric.roll_sharpe(window)

class ar(RollingStatistics):
    '''
    Calculate the realized annualized standard deviation (volatility) as percentage
    of the underlying value.
    '''
    name = 'Autocorrelation coefficient percentage volatility'
        
    def calculate(self, ts, window = 20, order = 1, **kwargs):
        order = safe_unsigned(order,1)
        d = ts.econometric.logdelta()
        return d.econometric.roll_ar(window,order)
    
    
class rcorr(RollingStatisticsN):
    
    '''
    Calculate the rolling percentage correlation of two timeseries.
    '''
    name = 'Rolling Correlation'
    
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

        
    