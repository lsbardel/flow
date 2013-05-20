
from jflow.core.pricers import Pricer



class EquityPricer(Pricer):
    
    def __init__(self):
        super(EquityPricer,self).__init__()
        
    def calculate(self, inst, rate):
        '''
        Perform calculation of a fund instrument
        '''
        hist   = inst.histories
        price  = hist.get('price',None)
        if price:
            ts = price.ts
            try:
                last = ts.back()
                inst.mktprice  = last[1]
                d = ts.econometric.slogdelta()
                inst.annualvol = d.econometric.vol()
            except:
                pass
            
        
        