#
# Retrive econometric data from JSON RPC SERVER
#
# Requires unuk
#
from dateutil.parser import parse as DateFromString
from unuk.core.jsonrpc import Proxy

def date2yyyymmdd(dte):
    return dte.day + 100*(dte.month + 100*dte.year)

def econometric_data(data,url):
    cts    = data.get('command',None)
    start  = data.get('start',None)
    end    = data.get('end',None)
    period = data.get('period',None)
    if start:
        start = date2yyyymmdd(DateFromString(str(start)).date())
    if end:
        end = date2yyyymmdd(DateFromString(str(end)).date())
    proxy = Proxy(url)
    return proxy.raw_history(cts,start,end)