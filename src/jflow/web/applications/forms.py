from django import forms
from django.contrib.auth.models import User

from djpcms.utils.uniforms import FormLayout, Html, Fieldset, inlineLabels, ModelFormInlineHelper
from djpcms.forms import ModelMultipleChoiceField
from djpcms.views.apps.tagging import TagField

from jflow.db.instdata.models import DataId, EconometricAnalysis, VendorId
from jflow.db.instdata.forms import DataIdForm, EconometricForm


class NiceDataIdForm(DataIdForm):
    tags   = TagField()
    
    layout = FormLayout()
    layout.inlines.append(ModelFormInlineHelper(DataId,VendorId,extra=4))


class InstrumentForm(forms.ModelForm):
    pass
