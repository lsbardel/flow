import datetime

from django import forms
from django.template import loader

from djpcms.views import appsite, appview
from djpcms.plugins import DJPplugin
from djpcms.utils import mark_safe
from djpcms.utils.html import FormHelper, Fieldset, ModelChoiceField

from jflow.db import geo
from jflow.db.instdata.models import DataId, Cash
from jflow.db.trade.models import FundHolder, Fund, PortfolioView, ManualTrade
from jflow.db.trade.forms import PortfolioViewForm, ManualTradeForm
        
        
class FundHolderApplication(appsite.ModelApplication):
    search = appview.SearchView(in_navigation = False)
    view = appview.ViewView(regex = '(?P<id>[-\.\w]+)')
    
    def objectbits(self, obj):
        return {'id': obj.code}
    
    def get_object(self, *args, **kwargs):
        try:
            id = kwargs.get('id',None)
            return self.model.objects.get(code = id)
        except:
            return None
        

class PortfolioViewView(appview.ViewView):
    
    def title(self, page, instance = None, **urlargs):
        obj = instance
        if page.application == 'fund-view': 
            if isinstance(instance,PortfolioView):
                obj = instance.fund
        return super(PortfolioViewView,self).title(page, instance = obj, **urlargs)


class FundApplication(appsite.ModelApplication):
    search = appview.SearchView(in_navigation = False)
    view   = PortfolioViewView(regex = '(?P<id>[-\.\w]+)')
    view2  = PortfolioViewView(regex = '(?P<view_id>\d+)', parent = 'view')
    
    def title_object(self, obj):
        if isinstance(obj,PortfolioView):
            return u'%s by %s' % (obj.name,obj.user)
        else:
            return u'%s' % obj
        
    def objectbits(self, obj):
        if isinstance(obj,Fund):
            return {'id': obj.code}
        else:
            return {'id': obj.fund.code,
                    'view_id': obj.id}
    
    def get_object(self, *args, **kwargs):
        try:
            code    = kwargs.get('id',None)
            view_id = kwargs.get('view_id',None)
            obj = self.model.objects.get(code = code)
            if view_id:
                vid = int(view_id)
                return obj.views.get(pk = vid)
            else:
                return obj 
        except:
            return None
        
    def viewurl(self, request, obj):
        '''
        Get the view url if available
        '''
        #TODO: change this so that we are not tide up with name
        try:
            vname = 'view'
            if isinstance(obj,PortfolioView):
                vname=  'view2'
            view = self.getapp(vname)
            if view and self.has_view_permission(request, obj):
                djp = view(request, instance = obj)
                return djp.url
        except:
            return None
        
    def render_object(self, djp):
        pass
        

    
class PortfolioViewApplication(appsite.ModelApplication):
    form = PortfolioViewForm
    form_withrequest = True
    _form_add        = 'add'
    
    add    = appview.AddView()
    
    def submit(self, instance, own_view):
        obj = None
        if isinstance(instance,PortfolioView):
            obj = instance
        return super(PortfolioViewApplication,self).submit(obj, own_view)


class SecurityTradeForm(ManualTradeForm):
    dataid = ModelChoiceField(DataId.objects, label = 'security')
    add_cash_trade = forms.BooleanField(initial = False, required = False)
    helper = FormHelper()
    
    helper.layout.add(Fieldset('dataid'),
                      Fieldset('fund','open_date','quantity','price','add_cash_trade',
                                css_class = Fieldset.inlineLabels))
    
    class Meta:
        fields = ['fund','open_date','quantity','price']
    
    def save(self, commit = True):
        self.instance.dataid = self.cleaned_data['dataid']
        return super(SecurityTradeForm,self).save(commit = commit)
        
        
        
        
class CashTradeForm(ManualTradeForm):
    currency = forms.ChoiceField(choices = geo.currency_tuples())
    
    helper = FormHelper()
    
    helper.layout.add(Fieldset('currency','fund','open_date','quantity', css_class = Fieldset.inlineLabels))
    
    class Meta:
        fields = ['fund','open_date','quantity']
    
    def save(self, commit = True):
        if commit:
            dataid = Cash.objects.create(curncy = self.cleaned_data['currency'])
            self.instance.dataid = dataid
        return super(CashTradeForm,self).save(commit = commit)
    

class ManualTradeApplication(appsite.ModelApplication):
    form = SecurityTradeForm
    form_withrequest = True
    
    add      = appview.AddView()
    add_cash = appview.AddView(regex = 'addcash', form = CashTradeForm)
    
    

#
#__________________________________________________ PLUGINS
class PortfolioForm(forms.Form):
    for_user = forms.BooleanField(initial = False, required = False)

def item_description(item):
    if isinstance(item, PortfolioView):
        d = u'%s <i>by %s</i>' % (item.name,item.user)
    else:
        d = item.description or item.code
    return mark_safe(d)

class PortfolioList(DJPplugin):
    name = "porfolio_list"
    description = "Team and portfolio list"
    form        = PortfolioForm
    
    def render(self, djp, wrapper, prefix, for_user = False, **kwargs):
        instance = djp.instance
        request  = djp.request
        appmodel = None
        items    = None
        if for_user:
            user = request.user
            try:
                trader = user.trader
                appmodel = appsite.site.for_model(Fund)
                items  = trader.fund_holder.funds.filter(parent = None)
            except:
                pass
        else:
            if not instance:
                appmodel = appsite.site.for_model(FundHolder)
                items = FundHolder.objects.filter(fund_manager = True)
            elif isinstance(instance,FundHolder):
                appmodel = appsite.site.for_model(Fund)
                items = instance.funds.filter(parent = None)
            elif isinstance(instance,Fund):
                appmodel = appsite.site.for_model(Fund)
                items = instance.views.all()
                    
        if items and appmodel:
            cts = []
            for item in items:
                url = appmodel.viewurl(request,item)
                cts.append({'url':url,
                            'name':item_description(item)})
            return loader.render_to_string('trade/team_list.html', {'items': cts})        
        
        return u''
    