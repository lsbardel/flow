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
        sdata = econometric_data(data,settings.LEAH_SERVER_URL)
        return http.HttpResponse(sdata, mimetype='application/javascript')


def change_type(self, djp):
    '''Ajax view to change instrument form'''
    form = self.get_form(djp)
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


slug_regex = '(?P<id>[-\.\w]+)'

class DataApplication(TagApplication):
    inherit   = True
    form      = NiceDataIdForm
    form_template = 'instdata/dataid_change_form.html'
    
    timeserie = TimeserieView(regex = 'timeserie')
    add       = DataAddView(regex = 'add', isplugin = False)
    edit      = DataEditView(regex = 'edit/%s' % slug_regex, parent = None)
    view      = appview.ViewView(regex = slug_regex, parent = None)
    
    def objectbits(self, obj):
        '''
        Get arguments from model instance used to construct url
        By default it is the object id
        @param obj: instance of self.model
        @return: dictionary of url bits 
        '''
        return {'id': obj.code}
    
    def get_object(self, *args, **kwargs):
        '''
        Retrive an instance of self.model for arguments.
        By default arguments is the object id,
        Reimplement for custom arguments
        '''
        try:
            id = kwargs.get('id',None)
            return self.model.objects.get(code = id)
        except:
            return None
    
    def instrument_form(self, request, instance):
        data     = request.POST or request.GET
        initial  = dict(data.items())
        ct = initial.get('content_type',None)
        if not ct and instance:
            ct = djp.instance.content_type
        if ct:
            try:
                ct = ContentType.objects.get(id = ct)
                model = ct.model_class()
                f = modelform_factory(model, InstrumentForm)
                minstance = None
                if instance and isinstance(model,instance.instrument):
                    minstance = instance.instrument
                return f(initial = initial, instance = minstance)
            except:
                return None
        else:
            return None
        
    def get_form(self, djp, **kwargs):
        iform = self.instrument_form(djp.request, djp.instance)
        f = super(DataApplication,self).get_form(djp, **kwargs)
        if iform:
            f.add(iform)
        return f
    

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
    
