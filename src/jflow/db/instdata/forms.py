from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from django.db.models import Q

from tagging.forms import TagField

import models as datamodels
from jflow.db.instdata.utils import ctids
from jflow.db.instdata.dynct import ExtraContentForm


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

    

class DataIdForm(ExtraContentForm):
    content_type = forms.ModelChoiceField(queryset = ctids(), 
                                          required = False,
                                          label = 'instrument',
                                          widget = forms.Select({'class':'ajax'}))
        
    class Media:
        css = {
            'all': ('instdata/layout.css',)
        }
        js = ['instdata/decorator.js']
            
    class Meta:
        model   = datamodels.DataId
        
    
    
    
    