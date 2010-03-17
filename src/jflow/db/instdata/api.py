#
#    API using django-piston
#
from django import http

from piston.resource import Resource
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, throttle
from piston.doc import documentation_view

from jflow import get_version
from jflow.db.instdata import models


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
    fields = ('code', 'description', 'type', 'country', 'ccy', 'firm_code', 'instrument')
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
    
    def create(self, request):
        pass
    
    
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
