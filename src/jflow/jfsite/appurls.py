from django.contrib.auth.models import User
from django import http
from django.forms.models import modelform_factory

from tagging.models import Tag
from jflow.db.instdata.models import DataId, EconometricAnalysis
from jflow.db.instdata.forms import DataIdForm, EconometricForm

from djpcms.conf import settings
from djpcms.utils import form_kwargs
from djpcms.utils.html import form, formlet
from djpcms.views import appsite, appview
from djpcms.views.user import UserApplication
from djpcms.views.apps.tagging import tagurl


class DataApplication(tagurl.TagApplication):
    inherit = True
    form    = DataIdForm
    add     = appview.AddView(regex = 'add', parent = None)
    edit    = appview.EditView(regex = 'edit/(?P<id>\d+)', parent = None)
    view    = appview.ViewView(regex = '(?P<id>[-\.\w]+)')
    
    class Media:
        css = {
            'all': ('instdata/layout.css',)
            }
        js = ['instdata/decorator.js']
    
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
        
    def get_form(self, djp, initial = None, **kwargs):
        instance   = djp.instance
        request    = djp.request
        mform      = modelform_factory(self.model, self.form)
        initial    = self.update_initial(request, mform, initial)
        f1, f2, f3, f4 = mform.make(request.user,
                                    **form_kwargs(request = djp.request,
                                                  instance = instance,
                                                  initial = initial))
        fhtml = form(method = self.form_method,
                     template = 'instdata/addform.html',
                     url = djp.url,
                     cn = 'aligned')
        if self.form_ajax:
            fhtml.addClass(self.ajax.ajax)
        wrapper = djp.wrapper
        layout  = None
        if wrapper:
            layout = wrapper.form_layout
        fhtml['dataid']         = formlet(form = f1, layout = layout)
        fhtml['vendorids']      = formlet(form = f2, layout = layout)
        fhtml['instrumenttype'] = formlet(form = f3, layout = layout, submit = self.submit(instance))
        fhtml['instdata']       = formlet(form = f4, layout = layout)
        return fhtml
    

class EconometricApplication(tagurl.TagApplication):
    inherit = True
    form = EconometricForm
    form_withrequest = True
    
    add     = appview.AddView(regex = 'add')
    #edit    = appview.EditView(regex = 'edit/(?P<id>\d+)', parent = None)
    view      = appview.ViewView(regex = '(?P<id>[-\.\w]+)')



    
#___________________________________ REGISTERING DYNAMIC APPLICATIONS
appsite.site.register(settings.USER_ACCOUNT_HOME_URL, UserApplication, model = User)
appsite.site.register('/data/', DataApplication, model = DataId)
appsite.site.register('/econometric/', EconometricApplication, model = EconometricAnalysis)

