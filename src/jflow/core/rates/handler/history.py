from datetime import datetime
from threading import Lock

from jflow.utils.decorators import threadSafe
from jflow.core.timeseries import dateseries, numericts
from jflow.core import dates
from jflow.core.dates import todate, toboostdate, date, get_livedate
from jflow.core.rates.objects import Rate


class cacheObject(object):
    '''
    Base class for all cache objects
    '''
    def __init__(self, cache):
        self.__cache = cache
        
    def __str__(self):
        return self.__class__.__name__
    
    def __get_cache(self):
        return self.__cache
    cache = property(fget = __get_cache)
    
    def log(self, msg, obj = None, verbose = 0):
        obj = obj or self
        self.cache.log(msg, obj, verbose = verbose)
        
    def err(self, msg, obj = None):
        obj = obj or self
        self.cache.err(msg, obj)


class rateHistoryBase(cacheObject):
    '''
    Object used to hold in memory an historical time-serie
    '''
    def __init__(self, cache, code, creator):
        super(rateHistoryBase,self).__init__(cache)
        '''
        code       rate ascii code
        holder     The cache object
        creator    The rate factory object
        '''
        self.__lastaccess     = datetime.now()
        self.lock             = Lock()
        self.__code           = code
        self.__factory        = creator
        self.__factory.holder = self
        self.flush()
        
    def __get_lastaccess(self):
        return self.__lastaccess
    lastaccess = property(fget = __get_lastaccess)
        
    def flush(self):
        '''
        Flush the memory cache
        '''
        self.__vendors        = {}
        self.live             = None
        
    def empty(self):
        return not (len(self.__vendors) or self.life) 
        
    def timeseries(self, vfid):
        '''
        in-memory time-series for vendor field 'vfid'
        
        @param vfid: vendor field id
        @see: jflow.core.rates.factory.factory.vendorfieldid 
        '''
        vendor = str(vfid.vendor)
        field  = str(vfid.field)
        self.__lastaccess = datetime.now()
        nts = None
        tss = self.__vendors.get(vendor,None)
            
        if tss == None:
            tss = {}
            self.__vendors[vendor] = tss
        else:
            nts = tss.get(field,None)
                
        if nts == None:
            name = str(vfid.code())
            if vfid.numeric:
                nts = numericts(name)
            else:
                nts = dateseries(name)
            
            tss[field] = nts
                
        return nts
    
        
    def clearlive(self, live_key):
        if self.live:
            self.live.clearlive(live_key)
    
    def __get_code(self):
        return self.__code
    code = property(fget = __get_code)
    
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.__factory)
    
    def __str__(self):
        return str(self.__repr__())
        
    def get(self, dte = None):
        dte = get_livedate(dte)
        if dte.live:
            return self.live
        else:
            try:
                return self.ts[dte.date]
            except:
                return None
    
    @threadSafe
    def add(self, r):
        if not isinstance(r, Rate):
            raise TypeError, '%r is not a Rate object' % r
        if r.live and self.live == None:
            self.live = r
        else:
            dte = r.date
            if not self.ts.has_key(dte):
                self.ts[dte] = r
    
    def get_or_make(self, dte, field = None, vendor = None):
        '''
        get a rate at date dte. If the rate is not available
        it creates it using the factory class
        '''
        dte    = get_livedate(dte)         
        rate   = self.get(dte)
        if rate != None:
            return rate
        # Rate not available, use factory to create one
        creator = self.factory
        if dte.live:
            rate = creator.make(dte)
            if rate != None:
                self.add(rate)
                rate.get(field,vendor)
        else:
            # historical rate
            return self.get_history(dte, dte, field = field, vendor = vendor)
        return rate
    
    def get_history(self,
                    start  = None,
                    end    = None,
                    field  = None,
                    vendor = None,
                    period = 'd',
                    parent = None):
        '''
        Call the factory class to load the history
        '''
        return self.factory.loadhistory(start,end,field,vendor,period=period,parent=parent)
    
    def register_to_rates(self, start=None, end=None, field=None, observer = None):
        '''
        Register an observer to a given rate
        '''
        start = get_livedate(start)
        end   = get_livedate(end)
        if start >= end:
            end = start
        if end.live:
            r = self.get_or_make(end,field)
            r.attach(observer)
        if start < end:
            return self.factory.loadhistory(start,end,field,observer=observer)
    
    def __get_factory(self):
        return self.__factory
    factory = property(fget = __get_factory)
    
    def __get_loaderpool(self):
        return self.cache.loaderpool
    loaderpool = property(fget = __get_loaderpool)
    
    def getts(self, start, end, vfid):
        ts    = self.timeseries(vfid)
        return ts.copy(start.date,end.date)
        #for d,v in ts.items():
        #    if d >= start:
        #        if d>end:
        #            break
        #        nv = v.get(field = field, vendor = vendor)
        #        if nv:
        #            ts[d] = nv
        #if liv and self.live:
        #    nv = self.live.get(field = field, vendor = vendor)
        #    if nv:
        #        ts[end] = nv
        #        
        #return ts
    
    def register_observer(self, start, end, field, observer):
        start = toboostdate(start.date)
        if end.live:
            end = dates.today()
        else:
            end   = toboostdate(end.date)
        for d,v in self.ts.items():
            if d >= start:
                if d>end:
                    break
                v.attach(observer)
        
        
    


class rateHistory(rateHistoryBase):
    '''
    Base class for historical rates
    '''    
    def __init__(self, *args):
        super(rateHistory,self).__init__(*args)
        
