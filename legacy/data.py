from django import http
from django.contrib.contenttypes.models import ContentType
from django.forms.models import modelform_factory

from djpcms.conf import settings
from djpcms.utils.ajax import jhtmls
from djpcms.views import appsite, appview
from djpcms.views.apps.tagging import TagApplication

from dynts.web.views import TimeserieView as TimeserieViewBase

from jflow.db.instdata.models import DataId, EconometricAnalysis, VendorId
from jflow.db.netdata.forms import ServerForm, ServerMachine
from jflow.web import forms



class TimeserieView(TimeserieViewBase):
    
    def getdata(self, code, start, end):
        server = ServerMachine.objects.get_for_machine('jflow-rpc')
        if server:
            proxy = server.get_proxy()
            try:
                return proxy.raw_history(cts,start,end)
            except IOError:
                return ''
        else:
            return ''
    
    def codeobject(self, object):
        return object.code


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
    form      = forms.NiceDataIdForm
    form_template = 'instdata/dataid_change_form.html'
    search_fields = ['code','name','description','tags','isin']
    
    timeserie = TimeserieView(regex = 'timeseries')
    complete  = appview.AutocompleteView()
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
        if not withdata:
            initial = initial or {}
            initial.update(dict(djp.request.POST.items()))
        f = super(DataApplication,self).get_form(djp, initial = initial, withdata = withdata, **kwargs)
        dataform = f.forms[0][1]
        iform    = dataform.content_form()
        if iform:
            f.add(iform)
        return f
    
    def object_from_form(self, form):
        if len(form.forms) == 2:
            form.forms.pop()
        return super(DataApplication,self).object_from_form(form)
    

class EconometricApplication(TagApplication):
    inherit = True
    form = forms.EconometricForm
    form_withrequest = True
    
    add     = appview.AddView(regex = 'add')
    #edit    = appview.EditView(regex = 'edit/(?P<id>\d+)', parent = None)
    view      = appview.ViewView(regex = '(?P<id>[-\.\w]+)')
    


class ServerApplication(appsite.ModelApplication):
    name    = 'Server Monitor'
    form    = ServerForm
    search  = appview.SearchView()
    add     = appview.AddView(regex = 'add', isapp = False)
    
    def object_content(self, djp, obj):
        c = super(ServerApplication,self).object_content(djp, obj)
        c['info'] = obj.get_info()
        return c
         
