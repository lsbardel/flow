from django.conf import settings
from jflow.utils.decorators import lazyattr
from jflow.db.instdata.models import DataId, Vendor, VendorId


class dataidhandler(object):
    
    def __init__(self):
        pass
    
    def default_vendor(self):
        return Vendor.objects.get(code = settings.DEFAULT_VENDOR_FOR_SITE)
    
    def setdefvendor(self):
        dfv = self.default_vendor()
        ids = DataId.objects.all()
        c   = 0
        n   = 0
        for id in ids:
            if id.default_vendor == None:
                vid = id.vendorid_set.filter(vendor = dfv)
                if vid:
                    id.default_vendor = dfv
                    id.save()
                    c += 1
                else:
                    n += 1
        return c,n
        
    
    def add(self, data):
        code = data.pop('code',None)
        if not code:
            raise ValueError, 'Code not available'
        id = DataId.objects.filter(code = code)
        if id.count():
            raise ValueError, 'Data Id %s already available' % code
        id = DataId(code = code,
                    name = data.pop('name',''),
                    description = data.pop('description',''),
                    default_vendor = data.pop('default_vendor',None),
                    country = data.pop('country',None),
                    live = data.pop('live',True),
                    tags = data.pop('tags',None))
        id.save()
        return id
    
    def addorget(self, data):
        code = data.get('code',None)
        id = DataId.objects.filter(code = code)
        if id.count():
            return id[0]
        else:
            return self.add(data)
    
    
    @lazyattr
    def vendors(self):
        ve = {}
        veds = Vendor.objects.all()
        for v in veds:
            ve[v.code] = v
        return ve
    
    def make_vendorid(self, ticker, v, id):
        '''
        Create a vendorId or update one
        '''
        if ticker and v:
            vid = id.vendorid_set.filter(vendor = v)
            if vid:
                vid = vid[0]
                vid.ticker = ticker
            else:
                vid = VendorId(dataid = id,
                               vendor = v,
                               ticker = ticker)
            vid.save()
            return vid
        else:
            return None
    
    def make_or_update_vendors(self, id, vd):
        '''
        Given a DataId id and a dictionary vd
         key   - vendor code
         value - vendorid ticker or Nothing
        '''
        if id == None:
            return
        for v in self.vendors().values():
            ticker = vd.pop(v.code,None)
            self.make_vendorid(ticker,v,id)

    def tags(self):
        from tagging.models import Tag
        ts = Tag.objects.usage_for_model(DataId, counts = True)
        return ts
