from baseoper import tsoperator
from math import log
from jflow.core import timeseries


class tsimple(tsoperator):
    
    class Meta:
        abstract = True
        
    def calculate(self,ts):
        raise NotImplemented
        
    def apply(self, ts):
        return self.unwind.tsData(data = self.calculate(ts))
        

class cctr(tsimple):
    '''
    Continuously compounded total return calculated as 100*log(v)
    '''
    fullname = 'Continuously Compounded Total Return'
    
    def calculate(self,ts):
        ns = self.newts()
        v0 = 0
        p  = 0
        for k,v in ts.items():
            va = 100*log(v)
            if p == 0:
                v0 = va
                p  = 1
            ns[k] = va - v0
            
        return ns
    

class lr(tsimple):
    '''
    Calculate the log return (percentage return) of a given timeseries
    '''
    usage = 'lr(x)'
    equivalent_to = 'delta(log(x))'
    
    def calculate(self,ts):
        return timeseries.logdelta(ts)
    
class delta(tsimple):
    '''
    Calculate the return of a given timeseries
    '''
    def calculate(self,ts):
        return timeseries.delta(ts)
    

class ptr(tsoperator):
    '''
    Percentage return        
    '''
    def calculate(self,ts):
        ns = self.newts()
        v1 = 0
        p = 0
        tmp_r = 0
        for k,v in ts.items():
            v0 = v1
            v1 = v
            if p == 1:
                tmp_r = (v1/v0-1)*100
                ns[k] = tmp_r
            else:
                p = 1
        return ns
        
    def apply(self,ts):
        
        ns = self.calculate(ts)        
        
        return self.unwind.tsData(data = ns)

    