from datetime import datetime
from threading import Lock

from jflow.core import dates
from jflow.utils.decorators import threadSafe

from history import *

__all__ = ['get_cache']

def TrimCodeDefault(code):
    return str(code).upper().replace(' ','_')
    

class rateCache(object):
    '''
    Rate Cache. This object should be used as a singleton.
    It maintains a financial rates in memory.
    The Rate factory must be implemented by applications
    '''
    def __init__(self, trimcode = None, minutecache = 5):
        '''
            vendorHandle  object for handling live data feeds from vendors
            gey_currency  function for retriving currency objects
            trimCode      function for trimming data IDs
        '''
        self.__timestart   = datetime.now()
        self.lock          = Lock()
        self.factory       = None
        self.loaderpool    = None
        self.vendorHandle  = None
        self.gey_currency  = None
        self.get_field     = None
        self.get_vendor    = None
        self.log_verbose   = 2
        self.logger        = None
        self.livecalc      = False
        self.minutecache   = minutecache
        self.trimCode      = trimcode or TrimCodeDefault
        self.__rates       = {}
    
    def __getitem__(self, key):
        '''
        Fetch a rate history object if available
        '''
        k = self.trimCode(key)
        return self.__rates.get(k,None)
    
    def get_livedate(self, dte):
        dte = dates.get_livedate(dte)
        if not self.livecalc and dte.live:
            return dates.get_livedate(dates.prevbizday())
        else:
            return dte            
    
    def clearlive(self, live_key):
        for r in self.__rates.values():
            r.clearlive(live_key)
            
    def flush(self):
        '''
        Close all connections and flush the memory
        '''
        now = datetime.now()
        mc  = self.minutecache
        nr  = {}
        for k,r in self.__rates.items():
            delta = now - r.lastaccess
            if delta.minutes >= mc:
                r.flush()
            else:
                nr[k] = r
        self.__rates = nr
    
    def clear(self):
        '''
        Close all connections and flush the memory
        '''
        for r in self.__rates:
            r.flush()
        self.__rates = {}
        
    def get(self, key, dte):
        ta = self[key]
        if ta:
            return ta.get(dte)
        else:
            return None
    
    def __newrate(self, code, creator, klass):
        '''
        Create a new rateHistory object
        '''
        if self.__rates.has_key(code):
            raise KeyError, '%s already in rateCache' % code
        else:
            ts = klass(self,code,creator)
            self.__rates[code] = ts
            return ts
    
    def newrate(self, code, creator):
        return self.__newrate(code, creator, rateHistory)
    
    @threadSafe
    def get_rate_holder(self, code):
        if code == None:
            return None
        code  = self.trimCode(code)
        rates = self[code]
        if rates == None:
            factory = self.factory
            if factory == None:
                raise ValueError, "Rate factory not available"
            creator = factory.select(code)
            if creator:
                rates = self.newrate(code, creator)
        return rates
    
    def log(self, msg, obj = None, verbose = 3):
        if self.logger and verbose <= self.log_verbose:
            obj = obj or self
            msg = '%s - %s' % (obj,msg)
            self.logger.msg(msg)
    
    def err(self, msg, obj = None):
        obj  = obj or self
        msgt = '%s - %s' % (obj,msg)
        if isinstance(msg,Exception):
            msg = msg.__class__(msgt)
        else:
            msg = msgt
        self.logger.err(msg)
            
    def __get_timestart(self):
        return self.__timestart
    timestart = property(fget = __get_timestart)
                

       
def get_cache():
    global _rateCache
    if _rateCache == None:
        _rateCache = rateCache()
    return _rateCache

def trimCode(code):
    cache = get_cache()
    return cache.trimCode(code)


_rateCache = None
