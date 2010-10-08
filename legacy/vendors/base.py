from datetime import timedelta
from ccy.tradingcentres import DateFromString

from jflow.db.instdata.models import MktData, MktDataCache
from twisted.internet import defer



class deferredLoader(defer.Deferred):
    '''
    Utility class for handling vendors with asyncronous
    loading mechanism, such as bloomberg
    '''
    def __init__(self, ci, vfid, start, end, d, hcache):
        defer.Deferred.__init__(self)
        self.ci     = ci
        self.vfid   = vfid
        self.start  = start
        self.end    = end
        self.hcache = hcache
        d.addCallbacks(self.historyarrived,self.historyfailure)

    def historyarrived(self, res):
        '''
        History has arrived from vendor
        '''
        try:
            #self.ci.historyarrived(self.vfid, res)
            result = self.ci.get_result(self.vfid, self.start, self.end, res, self.hcache)
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
    
    def history(self, vfid, start, end, hcache):
        '''
        Fetch historical data from data provider
        hcache is an istance to the caching class
        '''
        st = start
        ed = end
        result = self._history(vfid, st, ed)
        if isinstance(result,defer.Deferred):
            return deferredLoader(self, vfid, start, end, result, hcache)
        else:
            return self.get_result(vfid, start, end, result, hcache)
    
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
        raise NotImplementedError
        
    def historyfailure(self,failure):
        pass
    

class DatabaseVendor(DataVendor):
    
    def _history(self, vfid, startdate, enddate):
        '''
        This method should be implemented by derived classes.
        By default do nothing
        '''
        return MktData.objects.filter(vendor_id = vfid.vid,
                                      field = vfid.field,
                                      dt__gte = startdate,
                                      dt__lte = enddate)
        
    def updatehandler(self, vfid, start, end, result, hcache):
        ts      = hcache.timeseries(vfid)
        for obj in result:
            ts[obj.dt] = obj.mkt_value
        return ts
    

vendors = {}
