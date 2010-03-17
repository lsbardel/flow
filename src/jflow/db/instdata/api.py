#
#    API using django-piston
#
from piston.resource import Resource
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.utils import rc, throttle
 
from jflow.db.instdata.models import DataId

 
class DataIdHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'PUT')
    fields = ('code', 'description', 'type', 'country', 'ccy', 'firm_code', 'instrument')
    #anonymous = 'AnonymousDataIdHandler'
    model = DataId
 
    @classmethod
    def resource_uri(cls, dataid):
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
    
    
class AnonymousDataIdHandler(DataIdHandler, AnonymousBaseHandler):
    """
    Anonymous entrypoint for blogposts.
    """
    fields = ('code', 'description', 'content_type')
    
    
def urls(auth):
    from django.conf.urls.defaults import url, patterns
    
    dataapi = Resource(handler=DataIdHandler, authentication=auth)
    
    urlpatterns = patterns('',
                           url(r'^$', dataapi),
                           url(r'^(?P<code>.+)/$', dataapi),
                           #url(r'^data/(?P<emitter_format>.+)/$', dataapi),
                           #url(r'^data\.(?P<emitter_format>.+)', dataapi, name='blogposts'),
                           # automated documentation
                           #url(r'^$', documentation_view),
                           )
    return urlpatterns
