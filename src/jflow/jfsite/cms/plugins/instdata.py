from django.conf import settings
from django import forms
from django.template import loader

from djpcms.utils import mark_safe
from djpcms.plugins import DJPplugin
from djpcms.views import appsite

from jflow.conf import settings as jflow_settings 
from jflow.db.instdata.models import DataId
from jflow.core.timeseries import operators

    
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
