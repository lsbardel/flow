from base import *

__all__ = ['todate',
           'toboostdate',
           'qdatetodate',
           'date2yyyymmdd',
           'yyyymmdd2date',
           'get_date']

def get_date(dte):
    if dte:
        return todate(dte)
    else:
        return dte

def qdatetodate(dt):
    return date(dt.year,dt.month,dt.day)

def toboostdate(dt):
    return boostdate(dt.year,dt.month,dt.day)

def todate(dte):
    if isinstance(dte,date):
        return dte
    try:
        idte = int(dte)
        if idte > 10000000:
            return yyyymmdd2date(idte)
        else:
            return julian2date(idte)
    except:
        try:
            return qdatetodate(dte)
        except:
            return _string_to_date(dte)
    


def date2yyyymmdd(dte):
    return dte.day + 100*(dte.month + 100*dte.year)


def yyyymmdd2date(dte):
    try:
        y = dte / 10000
        md = dte % 10000
        m = md / 100
        d = md % 100
        return date(y,m,d)
    except:
        raise ValueError, 'Could not convert %s to date' % dte
    
def julian2date(dte):
    raise NotImplementedError, 'Julian date to date format not implemented'

def julian2yyyymmdd(dte):
    raise NotImplementedError, 'Julian date to yyyymmdd format not implemented'

