from modeltrack.models import Tracker

from djpcms.views.tagging.views import searchtagview

import tagentry


class view(searchtagview):
    '''
    Base search view class for market data
    '''
    MAX_LENGTH_TEXT = 300
            
    def title(self):
        bc = self.breadcrumbs('Market Data')
        return bc
    
    def make_result(self, request, r):
        return tagentry.entry(view = self, request = request, object = r)
            
    def empty_queryset(self, request):
        return Tracker.objects.get_latest_accessed(self.model, request)

        

