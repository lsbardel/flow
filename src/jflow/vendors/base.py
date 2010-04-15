from datetime import timedelta
from ccy.tradingcentres import DateFromString

from jflow.db.instdata.models import MktDataCache
from twisted.internet import defer



class deferredLoader(defer.Deferred):
    '''
    Utility class for handling vendors with asyncronous
    loading mechanism, such as bloomberg
    '''
    def __init__(self, ci, vfid, start, end, d):
        defer.Deferred.__init__(self)
        self.ci    = ci
        self.vfid  = vfid
        self.start = start
        self.end   = end
        d.addCallbacks(self.historyarrived,self.historyfailure)

    def historyarrived(self, res):
        '''
        History has arrived from vendor
        '''
        try:
            self.ci.historyarrived(self.vfid, res)
            result = self.ci.get_result(self.vfid, self.start, self.end)
            self.callback(result)
        except Exception, e:
            self.errback(e)
        
    def historyfailure(self, err):
        self.callback()


class DataVendor(object):
    '''
    Interface class for Data Vendors
    '''
    def __new__(cls, *args, **attrs):
        global vendors
        obj = super(DataVendor, cls).__new__(cls, *args, **attrs)
        obj.datawriters   = {}
        vendors[obj.code] = obj
        return obj
    
    def __repr__(self):
        return self.code + ' data vendor handler'
    
    def __get_code(self):
        return self.__class__.__name__
    code = property(fget = __get_code)
    
    def weblink(self, ticker):
        '''
        Provide a link to a web page
        '''
        return None
    
    def dbobj(self):
        from jflow.db.instdata.models import Vendor
        try:
            return Vendor.objects.get(code = self.code)
        except:
            return None
    
    def external(self):
        return True
    
    def hasfeed(self, live = False):
        return not live
    
    def connected(self):
        return [self]
    
    def connect(self):
        pass
        
    def isconnected(self):
        '''
        Return True if data vendor connection is available
        '''
        return True
        
    def cache_table(self):
        return MktDataCache
    
    def cache_factory(self):
        return self.cache_table().objects
    
    def get_cache(self, vfid):
        return self.cache_factory().filter(field = vfid.field, vendor_id = vfid.vid)
        
    def history(self, vfid, start, end, hcache):
        '''
        Fetch historical data from data provider
        hcache is an istance to the caching class
        '''
        cache = self.get_cache(vfid)
        st = start
        ed = end
        result = None
        
        if cache:
            p0 = cache.filter(dt__lte = st)
            
            if p0:
                lt  = cache.latest()
                ldt = lt.dt
                if ldt >= ed:
                    result = cache.filter(dt__gte = start).filter(dt__lte = end)
                else:
                    st = ldt + timedelta(1)
                    
        if result is None:
            result = self._history(vfid, st, ed)
            
            if isinstance(result,defer.Deferred):
                return deferredLoader(self, vfid, start, end, result)
            else:
                return self.get_result(vfid, start, end, result, hcache)
        else:
            return result
    
    def get_result(self, vfid, start, end, result, hcache):
        result = self.updatehandler(vfid, start, end, result, hcache)
        hcache.memorise(result)
        return result
    
    def value(self, ticker, dte = None, field = None):
        raise NotImplementedError
    
    def _history(self, vfid, startdate, enddate):
        '''
        This method should be implemented by derived classes.
        By default do nothing
        '''
        return None
    
    def registerlive(self, rate):
        raise NotImplementedError
        
    def _save(self, res):
        return res
    
    def updatehandler(self, vfid, start, end, result, hcache):
        
        return self.get_cache(vfid).filter(dt__gte = start).filter(dt__lte = end)
        
    def historyfailure(self,failure):
        pass

vendors = {}
