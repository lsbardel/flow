from datetime import date

from jflow.core.timeseries import numerictsv
from jflow.core.datavendor import google


_default_tickers = ['NASDAQ:GOOG',
                    'NASDAQ:YHOO',
                    'NASDAQ:MSFT',
                    'NASDAQ:INTC',
                    'NASDAQ:AAPL']


def get_multivariate(*tickers, **kwargs):
    M     = len(_default_tickers)
    start = kwargs.pop('startdate',20080101)
    end   = kwargs.pop('startdate',date.today())
    field = kwargs.pop('field','close')
    N     = min(M,kwargs.pop('series',2))
    tickers = list(tickers)
    s = len(tickers)
    j = 0
    while s < N:
        tickers.append(_default_tickers[j])
        j+=1
        s+=1
    
    ts = numerictsv()
    g  = google()
    for t in tickers:
        ts.addts(g.get(t,start,end,field))
    return ts
            