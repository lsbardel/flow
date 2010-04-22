import datetime

from django import forms

#from tools import get_trader
from models import Fund, PortfolioView


class AddTradeBase(forms.Form):
    '''
    Base Form to add a new trade
    '''
    portfolio = forms.ModelChoiceField(queryset = None)
    date      = forms.DateField(initial = datetime.date.today())
    
    def __init__(self, request = None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        self.trader = get_trader(request.user)
        portfolio = self.base_fields.get('portfolio')
        portfolio.queryset = Fund.objects.subfunds(self.trader.fund_holder)
        super(AddTradeBase, self).__init__(*args, **kwargs)
        
        
class PortfolioViewForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        request  = kwargs.pop('request',None)
        instance = kwargs.pop('instance',None)
        if request:
            self.user = request.user
        else:
            self.user = None
        self.fund = None
        if isinstance(instance,Fund):
            self.fund = instance
        elif isinstance(instance,PortfolioView):
            kwargs['instance'] = instance
        super(PortfolioViewForm,self).__init__(*args, **kwargs)
        if self.fund:
            self.initial['fund'] = self.fund.id
            self.fields['fund'] = forms.CharField(widget=forms.HiddenInput)
    
    class Meta:
        exclude = ['user']
        model   = PortfolioView
        
    def save(self, commit = True):
        if self.user:
            self.instance.user = self.user
        return super(PortfolioViewForm,self).save(commit = commit)
    