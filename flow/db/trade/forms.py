import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm

from jflow.db.trade.models import FundHolder, Fund, Trader, PortfolioView, ManualTrade

def get_trader(user):
    if user.is_authenticated():
        try:
            trader = user.trader
        except:
            f,c = FundHolder.objects.get_or_create(code = 'NA')
            trader = Trader(fund_holder = f, user = user)
            trader.save()
        if not user.is_active:
            return None
    else:
        return None
    return trader

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


class BaseFundUserForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        request  = kwargs.pop('request',None)
        instance = kwargs.pop('instance',None)
        if request:
            self.user = request.user
            get_trader(self.user)
        else:
            self.user = None
        self.fund = None
        if isinstance(instance,Fund):
            self.fund = instance
        elif isinstance(instance,PortfolioView):
            kwargs['instance'] = instance
        super(BaseFundUserForm,self).__init__(*args, **kwargs)
        if self.fund:
            self.initial['fund'] = self.fund.id
            self.fields['fund'] = forms.CharField(widget=forms.HiddenInput)
    
    def save(self, commit = True):
        if self.user:
            self.instance.user = self.user
        return super(BaseFundUserForm,self).save(commit = commit)


class ManualTradeForm(BaseFundUserForm):
    pass
    
        
class PortfolioViewForm(BaseFundUserForm):
    
    class Meta:
        exclude = ['user']
        model   = PortfolioView
        

class TraderForm(UserCreationForm):
    
    class Meta:
        model = Trader
        exclude = ['user']
    
            