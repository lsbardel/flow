from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from django.db.models import Q
from django.forms.models import modelform_factory

from tagging.forms import TagField

import models as datamodels
from jflow.db.instdata.utils import ctids


noselection_string = '------------'

def Instrument_Choices():
    '''
    Return a list of 2-elements tuple
    '''
    from scripts.instrument import dbmodels
    insts = dbmodels()
    inst_options = [('',noselection_string)]
    for ii in insts:
        meta = ii._meta
        inst_options.append((meta.module_name,capfirst(meta.verbose_name)))
    return inst_options


class UniqueCodeField(forms.CharField):
    
    def __init__(self, model = None, codename = 'code',
                 lower = True, rtf = '_', extrafilters = None, *args, **kwargs):
        self.model = model
        self.lower = lower
        self.rtf   = rtf
        self.extrafilters = extrafilters
        self.codename     = codename
        super(UniqueCodeField,self).__init__(*args, **kwargs)
        
    def clean(self, value):
        c = super(UniqueCodeField,self).clean(value)
        if self.model:
            c = self.trimcode(c)
            kwargs = self.extrafilters or {}
            kwargs[self.codename] = c
            obj = self.model.objects.filter(**kwargs)
            if obj.count():
                raise forms.ValidationError('%s with %s code already available' % (self.model,c))
        return c


class DataCodeField(UniqueCodeField):
    
    def __init__(self, *args, **kwargs):
        super(DataCodeField,self).__init__(model = datamodels.DataId, *args, **kwargs)
        
    def trimcode(self, value):
        return datamodels.TrimCode(value)


#class ShortAddForm(forms.Form):
#    '''
#    Form used to load a DataID from Google or Yahoo finance
#    '''
#    default_vendor = forms.ModelChoiceField(label = 'Vendor',
#                                            queryset = datamodels.Vendor.objects.filter(Q(code = 'google') | Q(code = 'yahoo')))
#    ticker = forms.CharField(min_length = 3, max_length = 32)
#    code   = DataCodeField(min_length = 3, max_length = 32, required = False)
#    type   = forms.ChoiceField(choices  = Instrument_Choices(),
#                               required = False,
#                               initial  = 'no-instrument')
#    tags   = TagField(label = 'Labels', required = False)


class DataIdForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(queryset = ctids(), 
                                          required = False,
                                          label = 'instrument',
                                          widget = forms.Select({'class':'ajax'}))
    
    def __init__(self, *args, **kwargs):
        super(DataIdForm,self).__init__(*args, **kwargs)
        self.inst_form = self.get_inst_form(*args, **kwargs)
        
    class Media:
        css = {
            'all': ('instdata/layout.css',)
        }
        js = ['instdata/decorator.js']
        
    def is_valid(self):
        vi = super(DataIdForm,self).is_valid()
        if self.inst_form:
            vi = self.inst_form.is_valid() and vi
            if vi:
                self.cleaned_data.update(self.inst_form.cleaned_data)
            else:
                self.errors.update(self.inst_form.errors)
        return vi
    
    def get_inst_form(self, *args, **kwargs):
        ct = self.instance.content_type
        if not ct:
            data = self.initial
            if not data:
                data = dict(self.data.items())
            ct = data.get('content_type',None)
            if ct:
                ct = ContentType.objects.get(id = int(ct))
        if ct:
            inst_model = ct.model_class()
            inst_form  = modelform_factory(inst_model)
            return inst_form(*args, **kwargs)
        else:
            return None        
        
    class Meta:
        model   = datamodels.DataId
        
    def save(self, commit = True):
        base = self._meta.model.objects
        if self.instance.has_pk():
            return base.modify(self.instance, commit = commit, **self.cleaned_data)
        else:
            return base.create(self.instance, commit = commit, **self.cleaned_data)
    
    @classmethod
    def make(cls, user, data = None, instance = None, **kwargs):
        f1 = cls(data = data, instance = instance, **kwargs)
        return (f1,None,None,None)
    
    
    