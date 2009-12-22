from djpcms.views.base import baseview

from jflow.db.instdata import models as jmodels
from jflow.core.dates import DateFromString, date2yyyymmdd
from jflow.db.utility.server import userproxyserver
from jflow.site.html.tsplot import tsplot


class simpledump(object):
    
    def __init__(self, str):
        self.data = str
        
    def dumps(self):
        return self.data


class view(baseview):
    '''
    Handle the timeseries view
    '''        
    def title(self):
        return 'Time-series Analysis - beta'
        
    def loadurl(self):
        return self.url
        
    def plot_data(self, request, data):
        cts    = data.get('command',None)
        start  = data.get('start',None)
        end    = data.get('end',None)
        period = data.get('period',None)
        if start:
            start = date2yyyymmdd(DateFromString(str(start)).date())
        if end:
            end = date2yyyymmdd(DateFromString(str(end)).date())
        proxy = userproxyserver(request.user)
        data = proxy.raw_history(cts,start,end)
        return simpledump(data)
    
    def view_contents(self, request, params):
        pl = tsplot(height = '500px')
        return {'content11': [pl]}