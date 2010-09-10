import datetime

from django import forms
from django.template import loader

from djpcms.utils import mark_safe
from djpcms.plugins import DJPplugin
from djpcms.views import appsite

from jflow.conf import settings 
from jflow.utils.anyjson import json
from jflow.db.trade.models import FundHolder, Fund, PortfolioView

from jflow import api


class PortfolioForm(forms.Form):
    for_user = forms.BooleanField(initial = False, required = False)

def item_description(item):
    if isinstance(item, PortfolioView):
        d = u'%s <i>by %s</i>' % (item.name,item.user)
    else:
        d = item.description or item.code
    return mark_safe(d)



class PortfolioList(DJPplugin):
    name = "porfolio-list"
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


class PortfolioApplicationForm(forms.Form):
    api_url = forms.CharField()
    height = forms.IntegerField(initial = 0, required = False)



class PortfolioApplication(DJPplugin):
    '''Display the position of a team base on some inputs specified by the plugin form 
    '''
    name = 'portfolio-application'
    description = 'Portfolio Application'
    form        = PortfolioApplicationForm
    
    class Media:
        css = {
               'all': ('djpcms/rightclickmenu/rightclickmenu.css',
                       'trade/portfolio/layout.css',
                       'trade/portfolio/themes/simple/style.css')
               }
        js = ['txdo/JSON.js',
              'txdo/Orbited.js',
              'txdo/protocol/stomp.js',
              'djpcms/rightclickmenu/rightclickmenu.js',
              'trade/portfolio/jquery.portfolio.js',
              'trade/portfolio/portfolio_actions.js']
        
    def render(self, djp, wrapper, prefix, api_url = '.', height = 0, **kwargs):
        height = abs(int(height or 0))
        instance = djp.instance
        request  = djp.request
        obj = api.get_portfolio_object(instance, request.user)
        id  = finins.get_object_id(obj,datetime.date.today())
        options = {}
        ctx = {'url': api_url,
               'id': id,
               'options': options,
               'fields': mark_safe(json.dumps(finins.fields()))}
        if height:
            options['height'] = height
        return loader.render_to_string('trade/portfolio-application.html', ctx)
