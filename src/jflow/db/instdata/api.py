#
#    API using django-piston
#
from django import http
from django.utils import simplejson as json
from django.db import transaction

from piston.resource import Resource
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, throttle
from piston.doc import documentation_view

from jflow import get_version
from jflow.db.instdata import models
from jflow.db.instdata.fields import slugify
from jflow.db.instdata.settings import DEFAULT_VENDOR_FOR_SITE

def strkeys(item):
    r = {}
    for key,value in item.items():
        r[str(key)] = value
    return r


class InfoHandler(AnonymousBaseHandler):
    
    def read(self, request, version = True):
        if version:
            return get_version()
        else:
            raise http.Http404


class VendorHandler(AnonymousBaseHandler):
    model = models.Vendor
    
    @classmethod
    def resource_uri(cls, dataid):
        return ('data', [ 'json', ])
    
    def read(self, request, code = None):        
        base = self.model.objects
        if code:
            return base.get(code = code.upper())
        else:
            return base.all()


class DataIdHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT')
    fields = ('code', 'description', 'type', 'country', 'curncy', 'firm_code', 'instrument')
    #anonymous = 'AnonymousDataIdHandler'
    model = models.DataId

    @classmethod
    def resource_uri(cls, code = None):
        return ('data', [ 'json', ])
    
    def read(self, request, code = None): 
        base = self.model.objects
        if code:
            return base.get(code = code.upper())
        else:
            params = dict(request.GET.items())
            type = params.get('type',None)
            if type == None:
                return base.all()
            elif type:
                return base.for_type(type)
            else:
                return base.filter(content_type = None)
    
    @transaction.commit_manually
    def create(self, request):
        '''
        The POST dictionary contains
         - source String indicating the data source
         - data a JSON string
        '''
        params = dict(request.POST.items())
        data   = json.loads(params.get('data',None))
        user   = request.user
        if isinstance(data,dict):
            data = [data]
        ids = []
        
        self.vendors = models.Vendor.objects.all()
        self.vdict = {}
        for v in self.vendors:
            self.vdict[v.code] = v
        
        committed = False
        if user.has_perm('instdata.add_dataid'):
            committed = True
        
        # Loop over items
        for item in data:
            item = strkeys(item)
            
            issuer = {}
            for k,v in item.items():
                ks = k.split('__')
                if len(ks) == 2 and ks[0] == 'issuer' and v:
                    issuer[ks[1]] = v
            
            # Check if we need to create an issuer
            if issuer:
                issuer, vi = self.createsingle(issuer)
                vi = ' --- %s' % vi
            else:
                issuer, vi = None,''
            
            id, v = self.createsingle(item)
            ids.append({'result':'%s%s' % (v,vi)})
        
        if committed:
            transaction.commit()
        else:
            transaction.rollback()
        
        return {'committed': committed,
                'result': ids}
    
    def createsingle(self, item):
        code = item.pop('code',None)
        idcode, vids = self.vids_from_data(item)
        if not code:
            code = idcode
        try:
            id, created = self.model.objects.get_or_create(code = code, **item)
            if created:
                v = 'Created %s' % id.code
            else:
                v = 'Modified %s' % id.code
            return id,v
        except Exception, e:
            return None,str(e)
        
    def vids_from_data(self, item):
        idcode = None
        vids = []
        idcodes = {}
        for code,v in self.vdict.items():
            name = item.get(code,None)
            if name:
                vids.append({'vendor': v,
                             'ticker': name})
                idcodes[code] = name
        vidcode = DEFAULT_VENDOR_FOR_SITE
        idcode  = idcodes.get(vidcode,None)
        if not idcode:
            for vidcode,idcode in idcodes:
                break
        if vidcode:
            return self.code_from_vendor(vidcode,idcode),vids
        return None, vids
    
    def code_from_vendor(self, vidcode, idcode):
        #TODO move thid at application level.
        if vidcode == 'BLB':
            idcode = idcode.split(' ')[:-1]
        else:
            idcode = idcode.split(' ')
        return slugify('_'.join(idcode).upper())
    
def urls(auth, baseurl = None):
    from django.conf.urls.defaults import url
    
    infoapi = Resource(handler=InfoHandler)
    vendapi = Resource(handler=VendorHandler)
    dataapi = Resource(handler=DataIdHandler, authentication=auth)
    
    if baseurl is None:
        baseurl = models.DataId._meta.app_label
    
    if baseurl:
        baseurl = '%s/' % baseurl
    else:
        baseurl = ''
    
    return (
            url(r'^%sversion/$' % baseurl, infoapi, {'version': True}),
            url(r'^%sdata/$' % baseurl, dataapi),
            url(r'^%sdata/(?P<code>.+)/$' % baseurl, dataapi),
            url(r'^%svendor/$' % baseurl, vendapi),
            url(r'^%svendor/(?P<code>.+)/$' % baseurl, vendapi),
            #url(r'^data/(?P<emitter_format>.+)/$', dataapi),
            #url(r'^data\.(?P<emitter_format>.+)', dataapi, name='blogposts'),
            # automated documentation
            url(r'^%s$' % baseurl, documentation_view),
            )
