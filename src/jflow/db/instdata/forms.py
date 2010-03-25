from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from django.db.models import Q

from tagging.forms import TagField

from models import DataId
from jflow.db.instdata.utils import ctids
from jflow.db.instdata.dynct import ExtraContentForm

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
        model   = DataId

    
    
    
    