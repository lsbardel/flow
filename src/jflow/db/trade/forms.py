import datetime

from django import forms

from tools import get_trader
from models import Fund

class AddTradeBase(forms.Form):
    '''
    Base Form to add a new trade
    '''
    portfolio = forms.ModelChoiceField(queryset = None)
    
    def __init__(self, request = None, *args, **kwargs):
        if request is None:
            raise TypeError("Keyword argument 'request' must be supplied")
        self.trader = get_trader(request.user)
        portfolio = self.base_fields.get('portfolio')
        portfolio.queryset = Fund.objects.subfunds(self.trader.fund_holder)
        super(AddTradeBase, self).__init__(*args, **kwargs)
        