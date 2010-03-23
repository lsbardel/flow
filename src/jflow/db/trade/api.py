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

import models

class FundHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    model = models.Fund
    fields = ('code', 'firm_code', 'description',
              'fund_holder', 'parent', 'curncy', 'dataid')
    
    def read(self, request, code = None, team = None):
        base = self.model.objects
        if code:
            try:
                return base.get(code = code.upper())
            except:
                return None
        elif team:
            return base.filter(fund_holder__code = team.upper())
        else:
            return base.all()
    
    
        

class PositionHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT')
    fields = ('code', 'description', 'type', 'country', 'curncy', 'firm_code', 'instrument')
    #anonymous = 'AnonymousDataIdHandler'
    model = models.Position
    
    


def urls(auth, baseurl = None):
    from django.conf.urls.defaults import url
    
    fundapi = Resource(handler=FundHandler, authentication=auth)
    
    if baseurl is None:
        baseurl = models.Position._meta.app_label
    
    if baseurl:
        baseurl = '%s/' % baseurl
    else:
        baseurl = ''
    
    return (
            #url(r'^%sversion/$' % baseurl, infoapi, {'version': True}),
            #url(r'^%stestdata/$' % baseurl, infoapi, {'testdata': True}),
            url(r'^%sfund/$' % baseurl, fundapi),
            url(r'^%sfund/(?P<code>.+)/$' % baseurl, fundapi),
            url(r'^%sfundteam/(?P<team>.+)/$' % baseurl, fundapi),
            #url(r'^%s$' % baseurl, documentation_view),
            )
