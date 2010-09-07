from django import http
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory

from flowrepo.models import Report

from djpcms.conf import settings
from djpcms.utils.ajax import jhtmls
from djpcms.views import appsite, appview
from djpcms.views.apps.tagging import TagApplication

from dateutil.parser import parse as DateFromString
from unuk.core.jsonrpc import Proxy

from jflow.db.instdata.models import DataId, EconometricAnalysis, VendorId
from jflow.jfsite.cms.applications.forms import NiceDataIdForm, ReportForm, EconometricForm, InstrumentForm


def date2yyyymmdd(dte):
    return dte.day + 100*(dte.month + 100*dte.year)

def econometric_data(data,url):
    cts    = data.get('command',None)
    start  = data.get('start',None)
    end    = data.get('end',None)
    period = data.get('period',None)
    if start:
        start = date2yyyymmdd(DateFromString(str(start)).date())
    if end:
        end = date2yyyymmdd(DateFromString(str(end)).date())
    proxy = Proxy(url)
    try:
        return proxy.raw_history(cts,start,end)
    except IOError:
        return ''


def getserver():
    #from jflow.db.netdata.models import ServerMachine
    #return ServerMachine.objects.get_for_machine('jflow-data-server')
    return 'http://localhost:9010/'

class TimeserieView(appview.AppView):
    '''
    view used to obtain timeseries.
    The only view available is an Ajax Get view
    '''
    _methods      = ('get',)
    
    def get_response(self, djp):
        request = djp.request
        if not request.is_ajax():
            raise http.Http404
        data = dict(request.GET.items())
        server = getserver()
        sdata = econometric_data(data,server)
        return http.HttpResponse(sdata, mimetype='application/javascript')


def change_type(self, djp):
    '''Ajax view to change instrument form'''
    form = self.get_form(djp, withdata = False)
    forms = list(form.forms_only())
    if len(forms) == 2:
        form = forms[1]
        html = form.layout.render(form)
    else:
        html = ''
    return jhtmls(html = html, identifier = '.data-id-instrument')



class DataAddView(appview.AddView):

    def ajax__content_type(self, djp):
        return change_type(self,djp)

class DataEditView(appview.EditView):

    def ajax__content_type(self, djp):
        return change_type(self,djp)
    
    def title(self, page, **urlargs):
        return u'edit'


slug_regex = '(?P<id>[-\.\w]+)'

class DataApplication(TagApplication):
    inherit   = True
    form      = NiceDataIdForm
    form_template = 'instdata/dataid_change_form.html'
    
    timeserie = TimeserieView(regex = 'timeseries')
    add       = DataAddView(regex = 'add', isplugin = False)
    view      = appview.ViewView(regex = slug_regex, parent = None)
    edit      = DataEditView()
    
    def objectbits(self, obj):
        return {'id': obj.code}
    
    def get_object(self, *args, **kwargs):
        try:
            id = kwargs.get('id',None)
            return self.model.objects.get(code = id)
        except:
            return None
    
    def instrument_form(self, request, instance, bound):
        data     = request.POST or request.GET
        initial  = dict(data.items())
        ct = initial.get('content_type',None)
        instrument = None
        imodel     = None
        if not ct and instance:
            instrument = instance.instrument
            if instrument:
                imodel = instrument.__class__
        if not imodel and ct:
            try:
                ct = ContentType.objects.get(id = ct)
                imodel = ct.model_class()
            except:
                pass
        if imodel:
            f = modelform_factory(imodel, InstrumentForm)
            if bound:
                return f(data = data, instance = instrument)
            else:
                return f(initial = initial, instance = instrument)
        else:
            return None
        
    def get_form(self, djp, withdata = True, initial = None, **kwargs):
        initial = initial or {}
        if not withdata:
            initial.update(dict(djp.request.POST.items()))
        f = super(DataApplication,self).get_form(djp, initial = initial, withdata = withdata, **kwargs)
        dataform = f.forms[0][1]
        iform    = dataform.content_form
        if iform:
            f.add(iform)
        return f
    
    def object_from_form(self, form):
        form.forms.pop()
        return super(DataApplication,self).object_from_form(form)
    

class EconometricApplication(TagApplication):
    inherit = True
    form = EconometricForm
    form_withrequest = True
    
    add     = appview.AddView(regex = 'add')
    #edit    = appview.EditView(regex = 'edit/(?P<id>\d+)', parent = None)
    view      = appview.ViewView(regex = '(?P<id>[-\.\w]+)')
    

from flowrepo.models import Report, Attachment, Image
from flowrepo.cms import FlowItemApplication, ReportApplication


#_______________________________________________________________________ MANUAL TRADE
class ManualTradeApplication(appsite.ModelApplication):
    search = appview.SearchView()
    add = appview.AddView()


#_______________________________________________________________________ REPORT  
    
class BlogApplication(ReportApplication):
    form_ajax = False
    inherit   = True
    _form_save       = 'save'
    _form_continue   = 'save and continue'
    name      = 'report'
    form      = ReportForm
    
    class Media:
        css = {
            'all': ('flowrepo/flowrepo.css',)
        }

class ItemApplication(FlowItemApplication):
    name      = 'items'
    
