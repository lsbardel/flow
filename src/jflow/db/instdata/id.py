from jflow.db.instdata.models import Vendor, DataId

def TrimCode(code):
    return str(code).upper()

def get_vendor(code):
    code = TrimCode(code)
    try:
        return Vendor.objects.get(code = code)
    except:
        return None

def getidobj(code):
    if isinstance(code,DataId):
        return code
    else:
        code = TrimCode(code)
        try:
            return DataId.objects.get(code = code)
        except:
            return None
        
def getid(code, vendor = None):
    id = getidobj(code)
    if id:
        return dbid(id,vendor)
    else:
        return None

class dbid(object):
    '''
    Wrapper for for DataId objects
    '''
    _default_field   = 'LAST_PRICE'
    fields_shortcuts = {'ASK' :'ASK_PRICE',
                        'BID' :'BID_PRICE',
                        'LOW' :'LOW_PRICE',
                        'HIGH':'HIGH_PRICE',
                        'OPEN':'OPEN_PRICE'}
    
    def __init__(self, id, vendor = None):
        '''
        id        DataId object
        vendor    a Vendor object, a vendor string code or None
        '''
        self.__id = id
        if vendor and not isinstance(vendor,Vendor):
            try:
                vendor = Vendor.objects.get(code = str(vendor))
            except:
                pass
        if not vendor:
            vendor = id.default_vendor
            
        self.__def_vendor   = vendor
        self.vendorids      = id.vendorid_set.all()
        self.__def_vendorid = self.vendorids.get(vendor = vendor)
        self.vendorList     = Vendor.objects.all()
        self.__vendor       = self.__def_vendor
    
    def default_field(self):
        return self._default_field
    
    def __str__(self):
        return str(self.__id)
    
    def __repr__(self):
        return str(self.__id)
    
    def __unicode__(self):
        return self.__id.__unicode__()
    
    def __get_code(self):
        return self.__id.code
    code = property(fget = __get_code)
        
    def vendorLoop(self, startvendor, field):
        flist = VendorDataField.objects.filter(field = field)
        f = flist.filter(vendor = startvendor)
        if f:
            return f[0]
        if flist:
            return flist[0]
        return None
    
    def testvendor(self, v):
        c = v.interface()
        if c and c.isconnected():
            vid = self.vendorids.filter(vendor = v)
            if vid:
                return vid[0]
        return None
    
    def avaiable_vendorid(self, field, vendor = None):
        '''
        Return the best possible vendor id and field
        '''
        if not isinstance(field,DataField):
            try:
                field = DataField.objects.get(code = field)
            except:
                return None
        # List of vendor datafield available for field field
        flist = VendorDataField.objects.filter(field = field)

        # If default vendor is available, start with it first
        vorder = []
        if isinstance(vendor,Vendor):
            vorder.append(vendor)
        if self.__def_vendor:
            vorder.append(self.__def_vendor)
            
        for v in vorder:
            vid    = self.testvendor(v)
            if vid:
                f      = flist.filter(vendor = v)
                if f:
                    return vfid(vid, f[0])
        
        # No luck with default vendor, try all others
        for f in flist:
            if f.vendor in vorder:
                continue
            vid = self.testvendor(f.vendor)
            if vid:
                return vfid(vid, f)
        
        return None
            
    
    def vendorid(self, field = None, vendor = None):
        vid = self.avaiable_vendorid(field,vendor)
        if not vid:
            return buildVendor(self.__id, field)
        else:
            return vid
    
    def history(self, startdate = None, enddate = None, field = None):
        vid = self.vendorid
        if vid == None:
            return None
        if enddate == None:
            enddate = date.today()
        if startdate == None:
            startdate = date(enddate.year-1,enddate.month,enddate.day)
        handler = vid.vendor.interface()
        return handler.history(vid,startdate,enddate,field)
    
    def instrument(self):
        '''
        Return a financial Instrument associated with this ID.
        None if not available.
        '''
        ic = self.__id.ic
        if ic:
            return ic.instrument()
        else:
            return None
        
    def vendors(self):
        return self.__id.vendorid_set.all()
    
    def get_vendorid(self, live = False):
        '''
        Get the appropriate vendor ID 
        '''
        if self.__def_vendor:
            v = self.__def_vendor
            c = v.interface()
            if c == None or not c.isconnected() or not c.hasfeed(live = live):
                # No interface for the vendor.
                # Pick another one
                vids = self.__id.vendorid_set.all()
                for vid in vids:
                    vv = vid.vendor
                    if vv == v:
                        continue
                    c = vv.interface()
                    if c and c.isconnected() and c.hasfeed(live = live):
                        return vid
                return None
            else:
                return self.__def_vendorid
            
    def get_field(self, field = None):
        '''
        Return a valid field code
        '''
        if field == None:
            field = self.default_field()
        elif isinstance(field, DataField):
            return field
        
        field = TrimCode(field)
        
        try:
            return DataField.objects.get(code = field)
        except:
            field = self.fields_shortcuts.get(field,None)
            if field:
                try:
                    return DataField.objects.get(code = field)
                except:
                    return None
            else:
                return None        
    
        
    
def parsets(cts, start, end, period = None):
    from jflow.core.timeseries.tscript import parse, createts
    cpars  = parse(cts)
    names  = cpars.names()
    ids    = {}
    for na in names:
        id = getid(na)
        if id:
            h  = id.history(start,end)
            ids[str(na)] = h
    return createts(cpars, ids)
    