from twisted.internet import defer

from jflow.core.dates import timedelta
from jflow.utils.decorators import runInThread


class loader(object):
    '''
    Helper class for loading data from a data provider
    '''
    def __init__(self, vid, field, vendor, st, ed):
        '''
            vid        VendorId object
            field      field string
            vendor     vendor interface
            st         start date
            ed         end date
        '''
        self.vid    = vid
        self.field  = self.get_field(field)
        self.start  = st
        self.end    = ed
        self.vendor = vendor
        
    def get_field(self, field):
        from jflow.db.instdata.models import DataField
        return DataField.objects.get(code = field)
        
    def load(self):
        from jflow.db.instdata.models import VendorDataField, MktDataCache
        
        if not self.vendor.external():
            return self.vendor._history(self.vid, self.start, self.end, self.field)
        else:
            fcode = VendorDataField.objects.get(field = self.field, vendor = self.vid.vendor)
            cache = MktDataCache.objects.filter(field = self.field, vendor_id = self.vid)
        
            st = self.start
            ed = self.end
        
            if cache.count():
                p0 = cache.filter(dt__lte = st)
            
                if p0.count():
                    lt  = cache.latest()
                    ldt = lt.dt
                    if ldt >= ed:
                        return cache.filter(dt__gte = self.start).filter(dt__lte = self.end)
                    else:
                        st = ldt + timedelta(1)
            
            d = self.vendor._history(self.vid.ticker, st, ed, fcode.code)
        
            if isinstance(d,defer.Deferred):
                return d.addCallbacks(self.historyarrived,self.historyfailure)
            else:
                return self.historyarrived(d)
        
    def historyarrived(self, res):
        from jflow.db.instdata.models import MktDataCache
        self.vendor.historyarrived(res)
        return MktDataCache.objects.filter(field     = self.field,
                                           vendor_id = self.vid,
                                           dt__gte   = self.start,
                                           dt__lte   = self.end)
        
    def historyfailure(self,failure):
        pass
    
    