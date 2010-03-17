from modeltrack.models import Tracker

from djpcms.views.tagging.views import objecttagview
from djpcms.html import link

from jflow.utils.decorators import lazyattr

from vendorlinks import vendorlinks, additionalidinfo, decomposition

class view(objecttagview):
    '''
    Data ID display view
    '''    
    def title(self):
        return u'%s - %s' % (self.object,self.object.country)
    
    def loadurl(self):
        tspage = Page.objects.get_for_code(code = 'TimeSeries')
        return tspage.get_absolute_url()
    
    def pokeobject(self, request):
        '''
        Poke the object
        '''
        from modeltrack.models import Tracker
        Tracker.objects.poke(request,self.object)
        return self.object
    
    def vendorlinks(self):
        return vendorlinks(self.object)
    
    def additionalinfo(self, request):
        return additionalidinfo(self.object,request)
    
    def decomposition(self, request):
        return decomposition(self.object,request)

