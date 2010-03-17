from django import forms
from django.utils.text import capfirst

from djpcms.html import AjaxSelect

from jflow.db.settings import FIRM_CODE_NAME
from jflow.db.instdata.scripts import instrument
import jflow.db.instdata.models as jmodels


__all__ = ['InstrumentChoice',
           'InstCodeForm',
           'DataIdForm',
           'VendorIdForm',
           'get_instrument_form']

noselection_string = '------------'

def Instrument_Choices():
    insts = instrument.dbmodels()
    inst_options = [('no-instrument',noselection_string)]
    for ii in insts:
        meta = ii._meta
        inst_options.append((meta.module_name,capfirst(meta.verbose_name)))
    return inst_options

class InstrumentChoice(forms.Form):
    select_instrument = AjaxSelect(choices  = Instrument_Choices(),
                                   required = False,
                                   initial  = 'no-instrument',
                                   label    = 'instrument')
    

class InstCodeForm(forms.Form):
    firm_code = forms.CharField(max_length=50, required = False, label=FIRM_CODE_NAME)
    
class DataIdForm(forms.ModelForm):
    class Meta:
        model = jmodels.DataId
    
#class VendorIdForm(forms.Form):
#    ticker = forms.CharField(max_length = 30)
#    vendor = forms.ChoiceField(choices = jmodels.Vendor.objects.all())
class VendorIdForm(forms.ModelForm):
    #data_id = forms.
    class Meta:
        model = jmodels.VendorId
        fields = ('ticker','vendor')
        
_instform = {}
class EquityForm(forms.ModelForm):
    class Meta:
        model = jmodels.Equity
_instform[jmodels.Equity] = EquityForm

class WarrantForm(forms.ModelForm):
    class Meta:
        model = jmodels.Warrant
_instform[jmodels.Warrant] = WarrantForm

class FundForm(forms.ModelForm):
    class Meta:
        model = jmodels.Fund
_instform[jmodels.Fund] = FundForm

class EtfForm(forms.ModelForm):
    class Meta:
        model = jmodels.Etf
_instform[jmodels.Etf] = EtfForm

class FutureForm(forms.ModelForm):
    class Meta:
        model = jmodels.Future
_instform[jmodels.Future] = FutureForm

class BondForm(forms.ModelForm):
    class Meta:
        model = jmodels.Bond
_instform[jmodels.Bond] = BondForm

class ForexForm(forms.ModelForm):
    class Meta:
        model = jmodels.Forex
_instform[jmodels.Forex] = ForexForm

class CashForm(forms.ModelForm):
    class Meta:
        model = jmodels.Cash
_instform[jmodels.Cash] = CashForm

class CashMiscForm(forms.ModelForm):
    class Meta:
        model = jmodels.CashMisc
_instform[jmodels.CashMisc] = CashMiscForm

def get_instrument_form(model):
    return _instform.get(model,None)