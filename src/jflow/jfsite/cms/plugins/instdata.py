from django.conf import settings
from django import forms
from django.template import loader

from djpcms.utils import mark_safe
from djpcms.plugins import DJPplugin
from djpcms.views import appsite

from jflow.conf import settings as jflow_settings 
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

