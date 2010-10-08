from jflow.db.instdata.models import DataField, VendorId
from base import DatabaseVendor
from ccy.data.ecb import ecbzipccy


class ecbwriter(object):
    
    def __init__(self, h, start, end):
        self.ecb      = h
        self.start    = start
        self.end      = end
        self.vendor   = self.ecb.dbobj()
        self.factory  = self.ecb.cache_factory()
        self.field    = DataField.objects.get(code = 'LAST_PRICE')
        self.vids     = {}
        
    def newccydata(self, cur, dte, value):
        if dte > self.end:
            return
        vid = self.vids.get(cur,None)
        if vid is None:
            try:
                vid = VendorId.objects.get(ticker = cur, vendor = self.vendor)
            except:
                vid = False
            self.vids[cur] = vid
        if vid:
            m = self.factory.get_or_create(vendor_id = vid, field = self.field, dt = dte)[0]
            m.mkt_value = value
            m.save()
    


class ecb(DatabaseVendor):
    '''
    European Central Bank market rates.
    The European central bank provides, free of charges, 
    market data and European area economic statistics. 
    '''
    pass
    
    

ecb()
