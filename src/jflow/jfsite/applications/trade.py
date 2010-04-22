import datetime

from django import forms

from djpcms.views import appsite, appview
from djpcms.utils.html import FormHelper, Fieldset, ModelChoiceField

from jflow.db.instdata.models import DataId
from jflow.db.trade.models import FundHolder, Fund, PortfolioView, ManualTrade
from jflow.db.trade.forms import PortfolioViewForm
        
        
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


class SecurityTradeForm(forms.ModelForm):
    date    = forms.DateField(initial = datetime.date.today())
    data_id = ModelChoiceField(DataId.objects)
    
    helper = FormHelper()
    
    helper.layout.add(Fieldset('data_id'),
                      Fieldset('date','quantity','price', css_class = Fieldset.inlineLabels))
    
    class Meta:
        fields = ['quantity','price']
            

class ManualTradeApplication(appsite.ModelApplication):
    form = SecurityTradeForm
    
    add = appview.AddView()
    