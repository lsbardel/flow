from django.contrib.auth.models import User

from djpcms import forms
from djpcms.utils.uniforms import FormLayout, Html, Fieldset, inlineLabels, ModelFormInlineHelper
from djpcms.views.apps.tagging import TagField

from jflow.db.instdata.models import DataId, EconometricAnalysis, VendorId
from jflow.db.instdata.forms import DataIdForm, EconometricForm
from jflow.db.trade.forms import PortfolioViewForm, ManualTradeForm
from jflow.db import geo

num_vendor_inlines = 4

class NiceDataIdForm(DataIdForm):
    tags   = TagField(required = False)
    
    layout = FormLayout()
    layout.inlines.append(ModelFormInlineHelper(DataId,VendorId,extra=num_vendor_inlines))


class InstrumentForm(forms.ModelForm):
    pass



class SecurityTradeForm(ManualTradeForm):
    dataid = forms.ModelChoiceField(DataId.objects, label = 'security')
    add_cash_trade = forms.BooleanField(initial = False, required = False)
    
    layout = FormLayout(Fieldset('dataid'),
                        Fieldset('fund','open_date','quantity','price','add_cash_trade',
                                 css_class = inlineLabels))
    
    class Meta:
        fields = ['fund','open_date','quantity','price']
    
    def save(self, commit = True):
        self.instance.dataid = self.cleaned_data['dataid']
        return super(SecurityTradeForm,self).save(commit = commit)
        
        
class CashTradeForm(ManualTradeForm):
    currency = forms.ChoiceField(choices = geo.currency_tuples())
    
    layout = FormLayout(Fieldset('currency','fund','open_date','quantity',
                                 css_class = inlineLabels))
    
    class Meta:
        fields = ['fund','open_date','quantity']
    
    def save(self, commit = True):
        if commit:
            dataid = Cash.objects.create(curncy = self.cleaned_data['currency'])
            self.instance.dataid = dataid
        return super(CashTradeForm,self).save(commit = commit)
    