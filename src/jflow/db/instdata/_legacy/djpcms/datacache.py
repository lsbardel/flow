from django import forms

from djpcms.views import Factory
from djpcms.html import quickform
from djpcms.settings import HTML_CLASSES

from jflow.db.instdata.models import MktDataCache


class InstCacheForm(forms.Form):
    data_id = forms.CharField(max_length=50, required = False)
    
    
def cacheform(data = None, initial = None, url = '', request = None):
    return quickform(form = InstCacheForm,
                     submitvalue = 'Clear',
                     submitname = 'clear_cache',
                     request = request,
                     url = url,
                     data = data,
                     initial = initial,
                     cn = HTML_CLASSES.ajax_form)



class view(Factory.childview):
    '''
     Clear the table containing the Data Cache
    '''
        
    def view_contents(self, request, params):
        return self.redirect_to(self.factoryurl())
    
    def get_form(self, data = None, request = None):
        if self.object and not data:
            initial = {'data_id':self.object.code}
        return cacheform(initial = initial, url = self.url, request = request)
        
    def has_permission(self, request):
        return request.user.is_superuser
    
    def clear_cache(self, request, data):
        f = self.get_form(request = request)
        MktDataCache.objects.emptycache(self.object)
        if self.object:
            msg = '%s cache cleared' % self.object
        else:
            msg = 'All market data cache was cleared'
        return f.messagepost(msg)