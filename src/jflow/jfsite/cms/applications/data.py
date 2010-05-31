from django import http, forms
from django.contrib.auth.models import User
from django.forms.models import modelform_factory

from tagging.models import Tag
from tagging.forms import TagField

from flowrepo.models import Report

from jflow.db.instdata.models import DataId, EconometricAnalysis, VendorId
from jflow.db.instdata.forms import DataIdForm, EconometricForm

from djpcms.conf import settings
from djpcms.utils import form_kwargs
from djpcms.utils.ajax import jhtmls
from djpcms.utils.html import htmlwrap, form, formlet, box, FormHelper, FormLayout, FormInlineHelper
from djpcms.utils.html import HtmlForm, Fieldset, ModelMultipleChoiceField, AutocompleteManyToManyInput
from djpcms.views import appsite, appview
from djpcms.views.apps.tagging import tagurl

from dateutil.parser import parse as DateFromString
from unuk.core.jsonrpc import Proxy


def AutocompleteTagField(required = False):
    wg = AutocompleteManyToManyInput(Tag, ['name'], separator = ' ', inline = True)
    return TagField(required = required, widget = wg)

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



class NiceDataIdForm(DataIdForm):
    tags   = AutocompleteTagField()
    
    helper = FormHelper()
    
    helper.inlines.append(FormInlineHelper(DataId,VendorId))
    
    # add the layout object
    helper.layout = FormLayout(
                             Fieldset('code', 'name', 'isin', 'firm_code', 'content_type',
                                      'tags', 'country',
                                      css_class = Fieldset.inlineLabels, key = 'main'),
                             Fieldset('description', key = 'descr'),
                             Fieldset('live', 'default_vendor',
                                      css_class = Fieldset.inlineLabels, key = 'second'),
                             template = 'instdata/dataid_change_form.html')

class InstrumentForm(forms.ModelForm):
    helper = FormHelper()

def change_type(djp):
    '''Ajax view to change instrument form'''
    view = djp.view
    request = djp.request
    obj  = djp.instance
    data = request.POST or request.GET
    initial = dict(data.items())
    form = view.appmodel.form(initial = initial, instance = djp.instance)
    iform = view.appmodel.instrument_form(request, form.content_form)
    if iform:
        iform = iform(initial = initial)
        html = iform.helper.layout.render(iform)
    else:
        html = ''
    data = jhtmls(html = html, identifier = '.data-id-instrument')
    return http.HttpResponse(data.dumps(), mimetype='application/javascript')

data_extra_views = {'content_type': change_type}
slug_regex = '(?P<id>[-\.\w]+)'

class DataApplication(tagurl.TagApplication):
    inherit   = True
    form      = NiceDataIdForm
    
    add       = appview.AddView(regex = 'add',
                                isplugin = False,
                                ajax_views = data_extra_views)
    timeserie = TimeserieView(regex = 'timeserie')
    edit      = appview.EditView(regex = 'edit/%s' % slug_regex,
                                 parent = None,
                                 ajax_views = data_extra_views)
    view      = appview.ViewView(regex = slug_regex)
    
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
    
    def instrument_form(self, request, content_form):
        if content_form:
            model = content_form._meta.model
            return modelform_factory(model, InstrumentForm)
        else:
            return None
        
    def get_form(self, djp, **kwargs):
        f = super(DataApplication,self).get_form(djp,**kwargs)
        f.instrument_form = self.instrument_form(djp.request, f.form.content_form)
        return f
        
    def get_form2(self, djp, initial = None, **kwargs):
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
    

from flowrepo.models import Report, Attachment, Image
from flowrepo.forms import FlowItemForm, add_related_upload
from flowrepo.cms import FlowItemApplication, ReportApplication
from flowrepo import markups

CRL_HELP = htmlwrap('div',
                    htmlwrap('div',markups.help()).addClass('body').render()
                   ).addClasses('flowitem report').render()

collapse = lambda title, html, c, cl: box(hd = title, bd = html, collapsable = c, collapsed = cl)



#_______________________________________________________________________ MANUAL TRADE
class ManualTradeApplication(appsite.ModelApplication):
    search = appview.SearchView()
    add = appview.AddView()





#_______________________________________________________________________ REPORT

class ReportForm(FlowItemForm):
    authors  = ModelMultipleChoiceField(User.objects, required = False)
    data_ids = ModelMultipleChoiceField(DataId.objects, required = False, label = 'Related securities')
    attachments  = ModelMultipleChoiceField(Attachment.objects, required = False, label = 'Available attachments',
                                            help_text = 'To select/deselect multiple files to attach press ctrl')
    images       = ModelMultipleChoiceField(Image.objects, required = False, label = 'Available images',
                                            help_text = 'To select/deselect multiple files to attach press ctrl')
    tags         = AutocompleteTagField()
    attachment_1 = forms.FileField(required = False)
    attachment_2 = forms.FileField(required = False)
    attachment_3 = forms.FileField(required = False)
    
    # Attach a formHelper to your forms class.
    helper = FormHelper()
    
    # add the layout object
    helper.layout = FormLayout(
                             Fieldset('name', 'description', 'body', key = 'body'),
                    
                             Fieldset('visibility', 'allow_comments',
                                      css_class = Fieldset.inlineLabels),
                            
                             Fieldset('authors', 'tags', 'data_ids'),
                             
                             HtmlForm(CRL_HELP, key = 'help',
                                      renderer = lambda html : collapse('Writing Tips',html,True,True)),
                            
                             Fieldset('attachments', 'images',
                                      key = 'current_attachments',
                                      renderer = lambda html : collapse('Attached files',html,True,False)),
                             
                             Fieldset('attachment_1', 'attachment_2', 'attachment_3',
                                      key = 'attachments',
                                      renderer = lambda html : collapse('New attachments',html,True,False)),
                                      
                             Fieldset('slug', 'timestamp', 'markup', 'parent',
                                      key = 'metadata',
                                      renderer = lambda html : collapse('Metadata',html,True,True)),
                    
                             template = 'flowrepo/report_form.html')
    
    def save(self, commit = True):
        instance = super(ReportForm,self).save(commit = commit)
        add_related_upload(self.cleaned_data['attachment_1'],instance)
        add_related_upload(self.cleaned_data['attachment_2'],instance)
        add_related_upload(self.cleaned_data['attachment_3'],instance)
        return instance
    
    class Meta:
        model = Report
    
    
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