from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.text import capfirst
from django.db.models import Q

from tagging.forms import TagField

from models import DataId, EconometricAnalysis
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
        

class EconometricForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request',None)
        if request:
            self.user = request.user
        else:
            self.user = None
        super(EconometricForm,self).__init__(*args, **kwargs)
        if self.user and not self.instance.pk:
            self.initial['user'] = self.user.id
            self.fields['user'] = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        exclude = ['user']
        model   = EconometricAnalysis
        
    def save(self, commit = True):
        if self.user:
            self.instance.user = self.user
        return super(EconometricForm,self).save(commit = commit)

    
    
    