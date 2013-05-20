from django import forms

from extracontent.forms import ExtraContentForm

from jflow.db.instdata.models import DataId, EconometricAnalysis
from jflow.db.instdata.utils import ctids


class DataIdForm(ExtraContentForm):
    content_type = forms.ModelChoiceField(queryset = ctids(), 
                                          required = False,
                                          label = 'instrument',
                                          widget = forms.Select({'class':'ajax'}))
            
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

    
    
    