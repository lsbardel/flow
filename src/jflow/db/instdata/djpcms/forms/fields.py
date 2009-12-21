from django import forms
from django.utils.text import capfirst
from django.db.models import Q

from djpcms.html import UniqueCodeField

from tagging.forms import TagField

from jflow.db.instdata.scripts.instrument import dbmodels
import jflow.db.instdata.models as datamodels


noselection_string = '------------'

def Instrument_Choices():
    '''
    Return a list of 2-elements tuple
    '''
    insts = dbmodels()
    inst_options = [('',noselection_string)]
    for ii in insts:
        meta = ii._meta
        inst_options.append((meta.module_name,capfirst(meta.verbose_name)))
    return inst_options

class DataCodeField(UniqueCodeField):
    
    def __init__(self, *args, **kwargs):
        super(DataCodeField,self).__init__(model = datamodels.DataId, *args, **kwargs)
        
    def trimcode(self, value):
        return datamodels.TrimCode(value)


class ShortAddForm(forms.Form):
    '''
    Form used to load a DataID from Google or Yahoo finance
    '''
    default_vendor = forms.ModelChoiceField(label = 'Vendor',
                                            queryset = datamodels.Vendor.objects.filter(Q(code = 'google') | Q(code = 'yahoo')))
    ticker = forms.CharField(min_length = 3, max_length = 32)
    code   = DataCodeField(min_length = 3, max_length = 32, required = False)
    type   = forms.ChoiceField(choices  = Instrument_Choices(),
                               required = False,
                               initial  = 'no-instrument')
    tags   = TagField(label = 'Labels', required = False)
    