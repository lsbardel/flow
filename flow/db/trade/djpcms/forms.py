import datetime

from django import forms

from djpcms.html import TradeDateField, UniqueCodeField

from jflow.db.trade.models import PortfolioView
    


class ChangeDate(forms.Form):
    date = TradeDateField(initial = datetime.date.today())


class FundForm(forms.Form):
    date   = TradeDateField()
    view   = forms.ModelChoiceField(None, required = True, empty_label = None)
    
    def __init__(self, instance = None, *args, **kwargs):
        if instance:
            self.base_fields['view'].queryset = instance
        super(FundForm,self).__init__(*args, **kwargs)
        
        
        
class AddNewView(forms.Form):
    name         = forms.CharField(max_length = 32)
    description  = forms.CharField(required = False)
    default      = forms.BooleanField(initial = False, required = False, help_text = "If set to true, the new view will be your default view for this portfolio.")
    copy_from    = forms.ModelChoiceField(None, required = False, help_text = "Copy initial subportfolios from another view.")
        
    def __init__(self, instance = None, *args, **kwargs):
        if instance:
            self.base_fields['copy_from'].queryset = instance
        super(AddNewView,self).__init__(*args, **kwargs)


class EditView(forms.Form):
    code         = UniqueCodeField(max_length = 32)
    name         = forms.CharField(required = False, max_length = 32)
    description  = forms.CharField(required = False)
    default      = forms.BooleanField(required = False, help_text = "If set to true, the new view will be your default view for this portfolio.")

    def __init__(self, instance = None, *args, **kwargs):
        if instance:
            f = self.base_fields['code']
            f.extrafilters = {'fund': instance.fund}
        super(EditView,self).__init__(*args, **kwargs)
        
class EditDefault(forms.Form):
    default      = forms.BooleanField(required = False, help_text = "If set to true, the new view will be your default view for this portfolio.")
    
    def __init__(self, instance = None, *args, **kwargs):
        super(EditDefault,self).__init__(*args, **kwargs)
        