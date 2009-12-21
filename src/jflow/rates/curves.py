
from qmpy.finance import dates
from qmpy.finance.settings import swapcurves
from qmpy.finance import ir


__all__ = ['swap_curve', 'ois_curve', 'swap', 'oiswap']


def swap(ccy, tenure):
    '''
    Create an interest rate swap
    '''
    fixed_freq = dates.parsefrequency(ccy.fixedfreq, tenure)
    float_freq = dates.parsefrequency(ccy.floatfreq, tenure)
    return ir.swap(ccy        = ccy,
                   tenure     = tenure,
                   fixed_freq = fixed_freq,
                   float_freq = float_freq,
                   fixed_dc   = ccy.fixeddc.code,
                   float_dc   = ccy.floatdc.code)
    
    
def oiswap(ccy, tenure):
    frequency = dates.parsefrequency(ccy.fixedfreq, tenure)
    return ir.oiswap(ccy       = ccy,
                     tenure    = tenure,
                     frequency = frequency,
                     dc        = ccy.floatdc.code)
    
    
    
class swap_curve(object):
    
    def __init__(self, cur):
        import prospero.db as DB
        self.cur   = DB.currency(cur)
        self.curve = swapcurves.get(str(self.cur),None)
        if self.curve == None:
            raise KeyError, 'No currency %s available' % self.cur
    
    def get(self):
        rates = []
        sws   = self.curve.swap.split(',')
        deps  = self.curve.depo.split(',')
        for s in sws:
            fi = swap(self.cur, s)
            rates.append(fi)
            
        for s in deps:
            fi = ir.deposit(ccy       = self.cur,
                            tenure    = s,
                            dc        = self.cur.floatdc.code)
            rates.append(fi)
            
        return rates
    
    
    
class ois_curve(swap_curve):
    
    def __init__(self, cur):
        super(ois_curve,self).__init__(cur)
    
    def get(self):
        rates = []
        sws  = self.curve.ois.split(',')
        for s in sws:
            fi = swap(self.cur, s)
            rates.append(fi)
            
        return rates


