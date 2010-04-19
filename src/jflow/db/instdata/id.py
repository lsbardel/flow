#
# High level interfaces for retriving data ids, datafield and vendors
#
#
from datetime import date

from django.core.cache import cache

from jflow.conf import settings
from jflow.db.instdata.models import Vendor, DataId, DataField, VendorDataField
from jflow.core.rates import vendorfieldid



def TrimCode(code):
    return str(code).upper().replace(' ','')

def get_code_cache(code, model, shortcuts = None):
    if isinstance(code,model):
        return code
    code = TrimCode(code)
    if shortcuts:
        code = shortcuts.get(code,code)
    key  = '%s:%s' % (model._meta,code)
    fdb  = cache.get(key,None)
    if not fdb:
        try:
            fdb = model.objects.get(code = code)
        except:
            return None
        cache.set(key,fdb)
    return fdb
    
def get_vendor(code = None):
    if not code:
        code = settings.DEFAULT_VENDOR_FOR_SITE
    return get_code_cache(code,Vendor)
        
def get_id(code):
    id = get_code_cache(code,DataId)
    if id:
        return dbid(id)
    else:
        return None
    
def get_field(field = None):
    '''
    Return a valid field proxy object
    '''
    if field == None:
        field = settings.DEFAULT_DATA_FIELD
    return get_code_cache(field,DataField,settings.FIELDS_SHORTCUTS)

def get_vendorfields_for_field(field):
    return VendorDataField.objects.filter(field = field)
    model = VendorDataField
    key  = '%s:forfield:%s' % (model._meta,field)
    fdb  = cache.get(key,None)
    if fdb is None:
        fdb = model.objects.filter(field = field)
        cache.set(key,fdb)
    return fdb



class vfid(vendorfieldid):
    
    def __init__(self, vid, vfield):
        field = vfield.field
        numeric = field.format == 'numeric'
        super(vfid,self).__init__(vid.dataid, vid, vfield.field, vfield, vid.vendor, numeric)
            


class dbid(object):
    '''
    Wrapper for for DataId objects
    '''    
    def __init__(self, id):
        '''
        id        DataId object
        vendor    a Vendor object, a vendor string code or None
        '''
        self.__id = id
        self.setup()
    
    def setup(self):
        vendor = self.__id.default_vendor
        if not vendor:
            vendor = get_vendor()
        self.def_vendor   = vendor
        self.vendorids    = self.__id.vendors.all()
        try:
            self.def_vendorid = self.vendorids.get(vendor = vendor)
        except:
            self.def_vendorid = None
        self.vendorList   = Vendor.objects.all()
    
    def __getstate__(self):
        return {'id':self.__id}
    
    def __setstate__(self,dict):
        self.__id = dict['id']
        self.setup()
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return str(self.__id)
    
    def __unicode__(self):
        return unicode(self.__id)
    
    def __get_code(self):
        return self.__id.code
    code = property(__get_code)
        
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
    
    def vendorid(self, field = None, vendor = None):
        return self.avaiable_vendorid(field,vendor)
    
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
        
    def vendors(self):
        return self.__id.vendorid_set.all()
    
    def get_vendorid(self, live = False):
        '''
        Get the appropriate vendor ID 
        '''
        if self.def_vendor:
            v = self.def_vendor
            c = v.interface()
            if c == None or not c.isconnected() or not c.hasfeed(live = live):
                # No interface for the vendor. Pick another one
                for vid in self.vendorids:
                    vv = vid.vendor
                    if vv == v:
                        continue
                    c = vv.interface()
                    if c and c.isconnected() and c.hasfeed(live = live):
                        return vid
                return None
            else:
                return self.__def_vendorid
        
    def avaiable_vendorid(self, field, vendor = None):
        '''
        Return the best possible vendor id and field
        '''
        if not field:
            return None
        flist = get_vendorfields_for_field(field)

        # If default vendor is available, start with it first
        vorder = []
        if isinstance(vendor,Vendor):
            vorder.append(vendor)
        if self.def_vendor:
            vorder.append(self.def_vendor)
            
        for v in vorder:
            vid    = self.testvendor(v)
            if vid:
                f = flist.filter(vendor = vid.vendor)
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
    
def parsets(cts, start, end, period = None):
    from jflow.core.timeseries.tscript import parse, createts
    cpars  = parse(cts)
    names  = cpars.names()
    ids    = {}
    for na in names:
        id = get_id(na)
        if id:
            h  = id.history(start,end)
            ids[str(na)] = h
    return createts(cpars, ids)
    