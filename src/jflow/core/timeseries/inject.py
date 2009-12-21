
from jflow import lib

_daycounters = {}


def codestr(self):
    return self.code

def injectdc(code,name,obj):
    obj.code = code
    obj.name = name
    obj.__str__  = codestr
    obj.__repr__ = codestr
    _daycounters[code] = obj 
    

injectdc('act360','Actual/360',lib.Act360())
injectdc('act365','Actual/365',lib.Act365())
injectdc('actact','Actual/Actual',lib.ActAct())
injectdc('30360','30/360',lib.thirty360())

def daycounter(code):
    return _daycounters.get(code,None)

__all__ = ['dateseries',
           'numericts',
           'numerictsv',
           'delta',
           'logdelta',
           'matrixseries',
           'toflot',
           'tsoper',
           'totsmatrix',
           'daycounter',
           'tsdaycount',
           'addition',
           'subtraction',
           'multiplication',
           'division']

dateseries   = lib.dateseries
numericts    = lib.numericts
matrixseries = lib.matrixseries
toflot       = lib.toflot
delta        = lib.delta
logdelta     = lib.logdelta

# Convert dictionary-type timeseries into a matrix time-series
# for fast econometric calculations
totsmatrix   = lib.totsmatrix

#tsoper       = lib.tsoper
tsoper       = numericts

def addition(self, other):
    pass
    #return lib.tsAdd(self,other)
def subtraction(self, other):
    pass
    #return lib.tsSubtract(self,other)
def multiplication(self, other):
    pass
    #return lib.tsMultiply(self,other)
def division(self, other):
    pass
    #return lib.tsDivide(self,other)
    

#numericts.__add__  = addition
#numericts.__sub__  = subtraction
#numericts.__mul__  = multiplication 
#lib.tsoper.__add__ = addition
#lib.tsoper.__sub__ = subtraction

def tsdaycount(ts, window, dc = 'actact'):
    dc = daycounter(dc)
    ite1 = ts.__iter__()
    for i in range(0,window):
        d1 = ite1.next()
        
    pe = []
    for d0 in ts:
        pe.append(dc.dcf(d0,d1))
        try:
            d1 = ite1.next()
        except:
            break
        
    return pe