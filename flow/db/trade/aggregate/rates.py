
from jflow.db.settings import DAYS_BACK, LIVE_CALCULATION
from jflow.core.dates import prevbizday
from jflow.rates import get_history


def history_dates(end):
    dt = end.dateonly
    if not LIVE_CALCULATION and end.live:
        dt = prevbizday(dt,1)
    start = prevbizday(dt,DAYS_BACK)
    return start, dt


class PortfolioRates(object):
    
    def __init__(self, cache):
        self.cache = cache
        self.rates = {}
        
    def get_data(self, code, end = None, **kwargs):
        '''
        Get the start date from end and DAYS_BACK
        '''
        code = str(code)
        ts = self.rates.get(code)
        start, end = history_dates(end)
        if ts:
            return ts
        h = get_history(code, start, end)
        return h
        #return h.addCallback(self.addhistory)
        
    def addhistory(self, res):
        try:
            self.rates[res.name] = res
        except:
            pass
        return res
        