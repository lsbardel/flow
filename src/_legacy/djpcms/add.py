from django.core.exceptions import ObjectDoesNotExist

from djpcms.settings import HTML_CLASSES
from djpcms.views import Factory
from djpcms.adminsite import get_admin_form, get_admin_form_class
from djpcms.html import form, formlet, makefkforms, submit, div, datatourl
from djpcms.ajax import jhtmls, jredirect

from jflow.db.instdata.scripts import instrument
from jflow.db.instdata.models import DataId, VendorId, InstrumentCode 

import forms


# Some css classes used throughout the view
css_class_instrument_form = 'instrument-form'
css_class_to_align_forms  = 'aligned'


class adddata(form):
    '''
    Form widget for adding DataId and Instruments.
    This form is an AJAX enabled form.
    '''
    def __init__(self, num_vendorids = 5, **attrs):
        self.instrument_form_class = 'instrument-form'
        self.num_vendorids = num_vendorids
        self.oldtype       = None
        self.newtype       = None
        super(adddata,self).__init__(**attrs)
        self.addclass(HTML_CLASSES.ajax_form)
        if not self.template:
            self.template = 'jflow/data/addform.html'
        
    def render(self):
        return self._render_template()
        
    def _make(self, data = None, **kwargs):
        '''
        Handle the internal form for adding DataId and Instruments.
        '''
        self.addclass(css_class_to_align_forms)
        co      = self.make_container()
        inst    = None
        subv    = "Add data ID"
        obj     = self.object
        dataty  = data
        
        if obj:
            ic = obj.ic
            if ic:
                inst = ic.instrument()
                if not inst:
                    ic.delete()
                    ic = None
                else:
                    if not data:
                        dataty = {'select_instrument': inst._meta.module_name}   
            subv = "Submit changes"
        
        # Instrument Form
        it = formlet(form = forms.InstrumentChoice,
                     data = dataty,
                     layout = 'flat',
                     submit = [submit(name='add_data', value=subv),
                               submit(name='cancel_data', value='Cancel')])
        it.is_valid()
        newtype = it.cleaned_data.get('select_instrument',None)
        newtype = instrument.get_instrument_model(newtype)

        # We create the main input formlets first
        dataid    = formlet(form   = forms.DataIdForm,
                                  model  = self.model,
                                  data   = data,
                                  object = obj)
        vendorids = makefkforms(form    = forms.VendorIdForm,
                                      model   = self.model,
                                      fkmodel = VendorId,
                                      object  = obj,
                                      data    = data,
                                      layout  = 'flat',
                                      extra   = self.num_vendorids)
        co['dataid'] = dataid
        co['vendorids'] = vendorids
        co['instrumenttype'] = it
        
        co['instdata']  = self.instrument_form(data,newtype)
    
        
    def instrument_form(self, data, newtype):
        '''
        Create the instrument form.
            instance is an instance of an instrument or None 
        '''
        co = div(cn = self.instrument_form_class)
        
        oldtype = None
        ic      = None
        inst    = None
        
        if self.object:
            ic    = self.object.ic
            if ic:
                inst    = ic.instrument()
                oldtype = inst.__class__ 
        
        # If an instrument is selected create the instruments forms
        if newtype:
            codedata = data
            if ic:
                fc = None
                if codedata:
                    fc = codedata.get('firm_code', None)
                if fc == None:
                    codedata = {'firm_code': ic.firm_code}
            co['code'] = formlet(form = forms.InstCodeForm, data = codedata)
            co['data'] = formlet(form   = forms.get_instrument_form(newtype),
                                 data   = data,
                                 object = inst)
    
        else:
            co.append('Data Id is not a tradable instrument')
        
        self.oldtype = oldtype
        self.newtype = newtype
        return co
        
    def save(self):
        '''
        save object to database
        '''
        id   = None
        code = None
        ic   = None
        data = None
        
        if self.object:
            oldid = self.object.code
            ic    = self.object.ic
            
        try:
            if not self.newtype or self.newtype.has_data_id:
                id        = self.dataid.save()
                for vidf in self.vendorids:
                    vidf.form.instance.dataid = id
                    vidf.save()
            else:
                code = self.dataid.cleaned_data.get('code')
                if not code:
                    raise ValueError
                
            instdata  = self.instdata
            
            if self.object:
                #
                # Check if the instrument has changed
                # If it did we need to destroy the old one
                if self.newtype != self.oldtype and ic:
                    ic.delete()
                    ic = None

            try:
                firm_code = instdata.code.cleaned_data.get('firm_code')
                data      = instdata.data.cleaned_data
            except:
                firm_code = None
                data      = None
            
            # We have instrument data. Create or modify instrument
            if data:                
                # We already have an instrument code.
                # We need to modify it.
                if ic:
                    ic.delete_instrument()
                    ic.code  = id.code
                    ic.save()
                    instrument.MakeInstrument(ic, firm_code = firm_code, **data)
                # We are creating a new instrument
                else:
                    instrument.Make(model     = self.newtype,
                                    dataid    = id,
                                    code      = code,
                                    firm_code = firm_code,
                                    user      = self.request.user,
                                    **data)
        except Exception, e:
            if id and id._get_pk_val() is not None:
                id.delete()
            raise ValueError, 'Error during saving: %s' % e
        
        return id
        

class view(Factory.childview):
    '''
     Add new data id to database.
     If the data id is a financial instrument, a new
     instrument will be also added to the database.
    '''
    authflag    = 'add'
        
    def title(self):
        return 'Add a new Data ID'
    
    def view_contents(self, request, params):
        '''
        contents in data-id home page
        '''
        bd = adddata(view = self, data = params, request = request)
        return {'form': bd}
    
    def select_instrument(self, request, params):
        '''
        Select a new instrument table and return a JSON html element
        '''
        f = adddata(view = self, request = request, data = params)
        return jhtmls(html = f.instdata.innerrender(),
                      identifier = '.%s' % f.instrument_form_class)
    
    def cancel_data(self, request, params):
        if self.object:
            return jredirect(self.factoryurl(request, 'view',self.object))
        else:
            return jredirect(self.factoryurl(request))
        
    def add_data(self, request, params):
        '''
        Add/Update data in database
        '''
        f = adddata(view = self, request = request, data = params)
        if f.is_valid():
            try:
                id = f.save()
            except Exception, e:
                return self.errorpost(e)
            return jredirect(self.factoryurl(request, 'view', id))
        else:
            # Try to save otherwise return errors
            try:
                id = f.save()
            except:
                return f.jerrors

    def add_short(self, request, params):
        '''
        Fetch security infiormation from the web and redirect
        to add page with relevant informations
        '''
        f = forms.shortaddform(request = request, data = params)
        if f.is_valid():
            data = f.cleaned_data
            try:
                dataval = instrument.createshort(data)
                mtyp    = dataval.pop('type',None)
                
                # Get the instrument type
                if mtyp:
                    dataval['select_instrument'] = mtyp
                    exch    = dataval.pop('exchange',None)
                    if exch:
                        dataval['exchange'] = exch.id
                        
                vendors = dataval.pop('vendors',None)
                if vendors:
                    c = 0
                    dv = dataval['default_vendor']
                    dataval['live'] = 'on'
                    dataval['default_vendor'] = dv.id 
                    for v,ticker in vendors:
                        dataval['%s-vendor' % c] = v.id
                        dataval['%s-ticker' % c] = ticker
                        c += 1
                return jredirect(datatourl(self.url,dataval))
            except Exception, e:
                return self.errorpost(e)
        else:
            return f.jerrors
