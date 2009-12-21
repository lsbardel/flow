
from qmpy.finance.dates import *

def future(code = default_future, date = today(), n = 0):
    return qmlib.future(code,date,n)

def futures(code = default_future, date = today(), n = 0):
    return qmlib.futures(code,date,n)

def irfuture(code = default_future, date = today(), n = 0):
    f = qmlib.future(code,date,n)
    return qmlib.interestratefuture(f)

def otcir(cur = 'eur', schedule = '6x9', start = today()):
    '''
    create a avanilla interest rate derivative
    This could be a FRA or a vanilla swap 
    '''
    ir = qmlib.interestrate(cur,schedule)
    fi = qmlib.otcir(ir,start)
    return fi.instrument

def finins(ins):
    try:
        return qmlib.fininswrap(ins)
    except:
        try:
            inner = ins.instrument
            return qmlib.fininswrap(inner)
        except:
            raise ValueError('%s is not an instrument' % ins)

    
def fwdcodes(tenure = 3, horizon = 3, dt = 0):
    '''
    Create a list of fwd rate codes
     - tenure    Rate tenure in months
     - horizon   Horizon in years
     - dt        time step in months (if <=0 tenure will be used)
    '''
    tenure = max(1,tenure)
    if dt <= 0:
        dt = tenure
    li = []
    cod = '%sM' % tenure
    li.append(cod)
    t = dt
    hm = 12*horizon
    while t < hm:
        li.append('%sx%s' % (t,t+tenure))
        t += dt
    return li

