from ccy.tradingcentres import prevbizday
from jflow.core import dates
from cache import get_cache, cacheObject
from factory import *
import objects

    
def splitcode(code):
    '''
    Four alternatives
    
    ticker
    ticker:field
    ticker:vendor
    ticker:field:vendor
    
    return
    ticker,field,vendor
    '''
    cache = get_cache()
    cd = code.split(':')
    if len(cd) == 2:
        v = cache.get_vendor(cd[1])
        if v:
            return cd[0],None,v
        else:
            return cd[0],cd[1],None
    if len(cd) == 3:
        f = cache.get_field(cd[1])
        if f:
            return cd[0],f,cd[2]
        else:
            f = cache.get_field(cd[2])
            if f:
                return cd[0],f,cd[1]
            else:
                v = cache.get_vendor(cd[1])
                if v:
                    return cd[0],None,v
                else:
                    return cd[0],None,cd[2]
    else:
        return code, None, None


def get_rate(code, dte = None):
    '''
    Fetch a single rate
    code is a string which specifies the data_id, the field (optional) and the
    vendor (optional)
    '''
    cache = get_cache()
    dte   = cache.get_livedate(dte)
    code, field, vendor = splitcode(code)
    rateholder = cache.get_rate_holder(code)
    if rateholder != None:
        return rateholder.get_or_make(dte,field,vendor)
    else:
        return None

def get_value(code, dte = None):
    '''
    Fetch a single rate
    '''
    code, field, vendor = splitcode(code)
    rate = get_rate(code,dte)
    if rate != None:
        return rate.get(field,vendor)
    else:
        return None
    
def get_history(code, start=None, end=None, field=None, period=None):
    '''
    Fetch a rate history
    '''
    cache = get_cache()
    start = cache.get_livedate(start)
    end   = cache.get_livedate(end)
    
    if start >= end:
        return get_value(code,start)
    
    if end.live:
        v = get_value(code, end)
        
    code, field, vendor = splitcode(code)
    rateholder = cache.get_rate_holder(code)
    if rateholder != None:
        return rateholder.get_history(start, end, field, vendor, period = period)
    else:
        return None
    
def get_analysis(cts, start = None, end = None, period = None, observer = None, json = False):
    return TimeseriesAnalysis(get_history, cts, start, end, period, observer, json)
    
    
def register_to_rates(code, start=None, end=None, field=None, observer = None):
    '''
    Fetch a single rate
    '''
    cache = get_cache()
    code, field = splitcode(code)
    rateholder = cache.get_rate_holder(code)
    if rateholder != None:
        rateholder.register_to_rates(start,end,field,observer=observer)



