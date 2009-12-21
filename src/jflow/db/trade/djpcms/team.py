'''
Team aggregate views.
    Aggregate portfolios across a management team
'''
import datetime

from django.http import Http404

from djpcms.settings import HTML_CLASSES
from djpcms.views import Factory
from djpcms.html import breadcrumbs, linklist, panel, quickform
from djpcms.ajax import simpledump, simplelem, jredirect

from jflow.db.utility.server import userproxyserver
from jflow.core.dates import date2yyyymmdd
from jflow.db.trade.utils import jsondisplays

from forms import ChangeDate


class teamview(Factory.childview):
    '''
    The aggregate view
    '''       
    def __get_team(self):
        return self.parentview.team
    team = property(fget = __get_team)
     
    def buildurl(self, dt, view):
        url1 = '%s/%02d/%02d/' % (dt.year,dt.month,dt.day)
        return '%s%s' % (self.childurlbase('view'),url1)
    
    def breadcrumbs(self):
        return self.parentview.breadcrumbs()
        
    def get_object(self, args):
        try:
            self.date = datetime.date(int(args[0]),int(args[1]),int(args[2]))
        except:
            raise Http404("Error in processing arguments, could not find date")
    
    def title(self):
        return self.breadcrumbs().render()
    
    def bread_crumbs_name(self):
        return self.page.href_name
    
    def viewform(self, data = None, initial = None, request = None):
        return quickform(form        = ChangeDate,
                         url         = self.url,
                         layout      = 'flat',
                         data        = data,
                         initial     = initial,
                         submitname  = 'change_view',
                         submitvalue = 'Refresh',
                         request     = request,
                         cn          = HTML_CLASSES.ajax_form)
        
    def view_contents(self, request, params):
        initial = {'date': self.date}
        f = self.viewform(initial = initial, request = request)
        return {'viewform': f.render(),
                'jsondisplays': jsondisplays(),
                'load_function': 'load_portfolio',
                'canmodify': 'false'}
        
    def change_view(self, request, params):
        '''
        Change protfolio date
        '''
        f = self.viewform(data = params, request = request)
        if f.is_valid():
            cd   = f.cleaned_data
            dt   = cd['date']
            url  = self.buildurl(dt)
            return jredirect(url)
        else:
            return jredirect(self.url)
        
    def load_portfolio(self, request, params):
        '''
        Post view to load portfolio
        '''
        proxy = userproxyserver(request.user)
        dt    = date2yyyymmdd(self.date)
        data  = proxy.raw_aggregates(self.team.code,dt)
        return simpledump(data)
    
    
     
     
class default_teamview(teamview):
    '''
    No date in the url, so we set it to today
    '''
    def __init__(self, *args, **kwargs):
        super(default_teamview,self).__init__(*args, **kwargs)
        
    def get_object(self, args):
        self.date   = datetime.date.today()

