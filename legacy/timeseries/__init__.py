
from jflow.lib import *
from parse import *
import math
import tests

def show(seq):
    for s in seq:
        print s
        
        
def round(v, p = 2):
    m = math.pow(10,p)
    return int(m*v)/m

def uloganalysis(ts, p = 2):
    v = univariate_loganalysis(ts)
    return {'Annualized Vol':  round(100*v[1],p),
            'Max Draw-Down':   round(100*v[4],p),
            'Skewness':        round(v[2],p),
            'Excess kurtosis': round(v[3],p)}
    
    
def safe_unsigned(num,default):
    try:
        num = int(num)
        num = max(0,num)
    except:
        num = default
    return num