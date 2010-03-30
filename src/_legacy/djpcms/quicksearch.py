from django.http import Http404

from djpcms.views import Factory
from djpcms.ajax import simplelem


class view(Factory.searchview):
    search_field_names = ['code','name']
    '''
    Quicksearch view. Only works for POST views
    '''        
    def get_view(self):
        raise Http404
    
    def post_view(self, request):
        '''
        Return a JSON list of entries
        '''
        params = dict(self.request.POST)
        q = params.get("q",None)
        limit = params.get("limit",100)
        qs    = self.get_query()
        if q:
            if isinstance(q,list):
                q = q[0]
            self.data_avail = True
            data = {'search': q}
            qs   = self.get_query(data)
        else:
            qs = []
        res = []
        if isinstance(limit,list):
            limit = limit[0]
        limit = int(limit)
        for q in qs[:limit]:
            res.append((q.code,str(q)))
        return self.return_post(simplelem(res))
        
            
            
        
        