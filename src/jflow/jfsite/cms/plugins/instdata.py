from django.conf import settings
from django import forms
from django.template import loader

from djpcms.utils import mark_safe
from djpcms.plugins import DJPplugin
from djpcms.views import appsite

from jflow.conf import settings as jflow_settings 
from jflow.db.trade.models import FundHolder, Fund, PortfolioView
from jflow.db.instdata.models import DataId
from jflow.core.timeseries import operators


#
#_____________________________________________________________________________ DATAID
class EcoForm(forms.Form):
    height = forms.IntegerField()
    
class EcoPlot(DJPplugin):
    name = "econometric-plot"
    description = "Econometric plot"
    form = EcoForm
    
    class Media:
        css = {
            'all': ('instdata/ecoplot/ecoplot.css',
                    'instdata/ecoplot/skins/smooth.css')
        }
        js = ['instdata/flot/excanvas.min.js',
              'instdata/flot/jquery.flot.js',
              'instdata/ecoplot/ecoplot.js']
    
    def render(self, djp, wrapper, prefix, height = 400, **kwargs):
        height = abs(int(height))
        instance = djp.instance
        ctx = {'url':'/data/timeserie/',
               'height':height}
        if isinstance(instance,DataId):
            ctx['code'] = instance.code
        return loader.render_to_string('instdata/econometric-plot.html', ctx)
    
    
class DataIdVendors(DJPplugin):
    name = "dataid_vendors"
    description = "Data ID vendors"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        instance = djp.instance
        if isinstance(instance,DataId):
            vids = instance.vendors.all()
            cts = []
            for v in vids:
                vendor = v.vendor
                vi = vendor.interface()
                tk = v.ticker
                if vi:
                    url = vi.weblink(tk)
                    cts.append({'url':url,
                                'vendor':v.vendor,
                                'ticker':v.ticker})
                    
            return loader.render_to_string('instdata/dataid_vendors.html', {'items': cts})
        else:
            return u''

class EconometricFunctions(DJPplugin):
    name = "econometric-functions"
    description = "Econometric Function"
    
    def render(self, djp, wrapper, prefix, **kwargs):
        ops = operators.all()
        rops = []
        for op in ops.values():
            rops.append({'operator': op.__name__,
                         'fullname': op.fullname,
                         'description': op.__doc__})
        return loader.render_to_string('instdata/operators.html', {'items': rops})



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