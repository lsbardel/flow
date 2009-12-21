
from datetime import date
from jflow import lib
from econometric import *



def iter_test():
    ts = lib.dateseries()
    d1 = date(2006,1,1)
    d2 = date(2005,2,10)
    d3 = date(2005,3,13)
    d4 = date(2005,4,16)
    d5 = date(2004,5,19)
    d6 = date(2004,6,20)
    d7 = date(2004,7,23)
    ts[3.5] = 'ciao'
    ts[3.2] = 'amico'
    ts[1.5] = 'mio'
    ts[2.5] = 'luca'

    for k in ts:
        print k
        
    for kv in ts.iteritems():
        print '%s  -  %s' % kv
        
        
def createts():
    ts = lib.numericts()
    ts[date(2006,1,1)]  = 3
    ts[date(2006,2,1)]  = 4
    ts[date(2006,1,5)]  = 6
    ts[date(2006,3,8)]  = -4
    ts[date(2006,6,10)] = 5
    ts[date(2006,9,20)] = -1
    ts[date(2006,7,1)]  = 0
    ts[date(2006,9,13)] = 12
    return ts

def matrix1():
    ts = createts()
    tv = lib.numerictsv()
    tv.addts(ts)
    return tv.tomatrix()
        

def oper_test1():
    from jflow.vendors import get_vendor
    google = get_vendor('google')
    t1 = google.history('LON:VOD',date(2008,1,1),date(2008,12,1))
    t2 = google.history('LON:BARC',date(2008,1,1),date(2008,12,1))
    t3 = t1 + t2
    t4 = t1 - t2
    t5 = 3 + t1
    
def oper_test():
    ts = numericts()
    ts[date(2008,1,1)] = 3
    ts[date(2008,1,3)] = 4
    return ts+1
    

    
def matrix_test(masked = False):
    '''
    Create a timeserie matrix from 2 timeseries
    '''
    from jflow.vendors import get_vendor
    google = get_vendor('google')
    t1 = google.history('LON:VOD',date(2008,1,1),date(2008,12,1))
    t2 = google.history('LON:BARC',date(2007,10,1),date(2008,11,28))
    mat = totsmatrix([t1,t2])
    return mat
    
    
    