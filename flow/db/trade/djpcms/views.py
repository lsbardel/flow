import datetime

from django.http import Http404
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from djpcms.settings import HTML_CLASSES
from djpcms.views import Factory
from djpcms.html import breadcrumbs, linklist, panel, feeds, quickform
from djpcms.ajax import simpledump, simplelem, jredirect

#from jflow.db.trade.portfolio import createportfolio
#from jflow.db.trade.models import Position, FundHolder
#from jflow.site.html import portfolio

from jflow.db.trade.models import PortfolioView, Fund, FundHolder
from jflow.db.trade.tools import get_trader
from jflow.db.trade.utils import jsondisplays, get_object_from_id, get_object_id
from jflow.db.utility.server import userproxyserver
from jflow.core.dates import date2yyyymmdd
from jflow.quickutils.djutils import todict 

from forms import FundForm, AddNewView, EditView, EditDefault


class basefundview(Factory.childview):
    
    def buildurl(self, dt, view):
        url1 = '%s/%s/%02d/%02d/' % (view.code,dt.year,dt.month,dt.day)
        return '%s%s' % (self.childurlbase('view'),url1)
    
    def __get_fund(self):
        return self.factory.fund
    fund = property(fget = __get_fund)
    
    def __get_team(self):
        return self.factory.team
    team = property(fget = __get_team)


class fundview(basefundview):
    '''
    View for a given Management Team' portfolio
    '''        
    def title(self):
        return self.breadcrumbs().render()
    
    def bread_crumbs_name(self):
        return '%s' % self.fund
        #return '%s - %s by %s' % (self.factory.fund.description, self.object.name, self.object.user)
    
    def bread_crumbs_parent(self):
        return self.factory.bread_crumbs_parent()
    
    def preprocess_default(self, request):
        '''
        used by the default view for retriving user informations
        '''
        pass
    
    def get_object(self, args):
        if args:
            code = args[0]
            try:
                self.date = datetime.date(int(args[1]),int(args[2]),int(args[3]))
            except:
                raise Http404("Error in processing arguments, could not find date")
            obj = self.fund.portfolioview_set.filter(code = code)
            if obj:
                self.object = obj[0]
            else:
                raise Http404("View %s for %s, not available" % (code,self.fund))
        else:
            raise Http404, "Error in processing argumnets, could not find a model"
        
    def get_trader(self):
        trader = get_trader_or_none(self.request.user)
        if not trader:
            raise PermissionDenied
        return trader
            
    def viewform(self, request = None, data = None, initial = None):
        return quickform(form     = FundForm,
                         view     = self,
                         layout   = 'flat',
                         data     = data,
                         initial  = initial,
                         request  = request,
                         object   = self.fund.portfolioview_set,
                         submitname = 'change_view',
                         submitvalue = 'Change view',
                         cn          = HTML_CLASSES.ajax_form)
    
    def view_contents(self, request, params):
        self.preprocess_default(request)
        initial = {'date': self.date,
                   'view': self.object.id}
        f = self.viewform(request = request, initial = initial)
        d = {'viewform': f.render(),
             'jsondisplays': jsondisplays(),
             'canmodify': 'false'}
        addview  = self.newchildview(request, 'add')
        editview = self.newchildview(request, 'edit', self.object)
        
        if request.user == self.object.user:
            d['canmodify'] = 'true'
        if addview:
            d['addform'] = addview.addform(request).render()
        if editview:
            d['editform'] = editview.editform(request).render()
        return d
        
    def change_view(self, request, params):
        '''
        Change protfolio view or date
        '''
        self.preprocess_default(request)
        f = self.viewform(request = request, data = params)
        if f.is_valid():
            cd   = f.cleaned_data
            dt   = cd['date']
            view = cd['view']
            url  = self.buildurl(dt,view)
            return jredirect(url)
        else:
            return jredirect(self.url)
        
    
    def load_portfolio(self, request, params):
        '''
        Post view to load portfolio
        '''
        self.preprocess_default(request)
        proxy = userproxyserver(request.user)
        dt    = date2yyyymmdd(self.date)
        data  = proxy.raw_portfolio(self.object.id,dt)
        return simpledump(data)
    
    def add_folder(self, request, params):
        '''
        Post view to add a folder
        '''
        self.preprocess_default(request)
        data  = todict(params)
        code  = data.get('code',None)
        pid   = data.get('parent',None)
        dt    = date2yyyymmdd(self.date)
        proxy = userproxyserver(request.user)
        return simpledump(proxy.raw_addfolder(self.object.id, dt, code, pid))
    
    def edit_folder(self, request, params):
        '''
        Post view to edit folder
        '''
        self.preprocess_default(request)
        data  = todict(params)
        dt    = date2yyyymmdd(self.date)
        proxy = userproxyserver(request.user)
        return simpledump(proxy.raw_editfolder(self.object.id, dt, data))
    
    def remove_folder(self, request, params):
        '''
        Post view to add a folder
        '''
        self.preprocess_default(request)
        data  = todict(params)
        id    = data.get('id',None)
        dt    = date2yyyymmdd(self.date)
        proxy = userproxyserver(request.user)
        return simpledump(proxy.raw_removePortfolioNode(self.object.id, dt, id))
    
    def move_node(self, request, params):
        self.preprocess_default(request)
        data   = todict(params)
        id     = data.get('id',None)
        target = data.get('target',None)
        dt     = date2yyyymmdd(self.date)
        proxy  = userproxyserver(request.user)
        return simpledump(proxy.raw_movePortfolioNode(self.object.id, dt, id, target))
    
    def market_risk(self, request, params):
        self.preprocess_default(request)
        data   = todict(params)
        id     = data.get('id',None)
        dt     = date2yyyymmdd(self.date)
        proxy  = userproxyserver(request.user)
        return simpledump(proxy.raw_marketRisk(self.object.id, dt, id))
        

class defaultfundview(fundview):
    '''
    The default fund view.
    We do not have any information about the view.
    '''
    def incache(self):
        return False
        
    def get_object(self, args):
        self.object = None
        self.date   = datetime.date.today()
            
    def preprocess_default(self, request):
        #First check if user has a default view
        if self.object:
            return
        manager     = PortfolioView.objects
        self.object = manager.get_default(request.user, self.fund)
        
        #Othervise get the default view
        if not self.object:
            view = manager.filter(fund = self.factory.fund, default = True)
            if not view.count():
                view = self.factory.make_default_view()
            else:
                view = view[0]
            self.object = view
        

class addfundview(basefundview):
    authflag      = 'add'
        
    def addform(self, request, data = None):
        return quickform(form        = AddNewView,
                         view        = self,
                         data        = data,
                         object      = self.factory.fund.portfolioview_set,
                         submitname  = 'create_view',
                         submitvalue = 'Create',
                         request     = request,
                         cn          = HTML_CLASSES.ajax_form)
        
    def create_view(self, request, params):
        f = self.addform(request, data = params)
        if f.is_valid():
            cd   = f.cleaned_data
            name = cd.get('name')
            des  = cd.get('description')
            nview = PortfolioView(code = name,
                                  name = name,
                                  description = des,
                                  user = request.user,
                                  fund = self.fund)
            nview.save()
            if cd.get('default',False):
                nview.set_as_default(request.user)
            
            cfrom  = cd.get('copy_from',None)
            if cfrom:
                folders = cfrom.portfolio_set.filter(Q(parent__isnull=True))
                for f in folders:
                    f.copytoview(nview)
            
            dt   = datetime.date.today() 
            url  = self.buildurl(dt,nview)
            return jredirect(url)
        else:
            return f.jerrors
        
        
class editfundview(basefundview):
    authflag      = 'change'
        
    def editform(self, request, data = None):
        initial = None
        default = self.object.is_default(request.user)
        fform   = EditView
        if data == None:
            if self.object.user == request.user:
                initial = {'code': self.object.code,
                           'name': self.object.name,
                           'description': self.object.description,
                           'default': default}
            else:
                initial = {'default': default}
        
        if self.object.user != request.user:
            fform = EditDefault
            
            
        return quickform(form        = fform,
                         view        = self,
                         data        = data,
                         instance    = self.object,
                         initial     = initial,
                         submitname  = 'edit_view',
                         submitvalue = 'Change',
                         request     = request,
                         cn          = HTML_CLASSES.ajax_form)
        
    def edit_view(self, request, params):
        f = self.editform(request, data = params)
        if f.is_valid():
            cd    = f.cleaned_data
            obj   = self.object
            if cd.get('default',False):
                obj.set_as_default(request.user)
            
            if self.object.user == request.user:
                obj.code  = cd.get('code')
                obj.name  = cd.get('name')
                obj.des   = cd.get('description')
                obj.save()            
            dt   = datetime.date.today()
            url  = self.buildurl(dt,obj)
            return jredirect(url)
        else:
            return f.jerrors
        
        
        
class fundviewfactory(Factory.view):
    '''
    Factory view class for a fund
    '''
    default_view_name   = 'default'
    default_system_uder = None
    
    def get_object(self, args):
        try:
            self.fund = Fund.objects.get(code = args[0])
        except:
            raise Http404
        
    def bread_crumbs_parent(self):
        return self.parentview.bread_crumbs_parent()
        
    def make_default_view(self):
        '''
        Create a default view.
        This can be reimplemented by derived classes
        '''
        try:
            user = User.objects.get(username = self.default_system_uder)
        except:
            raise Http404
        view = PortfolioView(name = self.default_view_name,
                             user = user,
                             fund = self.fund,
                             default = True)
        view.save()
        return view
    
    def __get_team(self):
        return self._get_team_impl()
    team = property(fget = __get_team)
    
    def _get_team_impl(self):
        raise NotImplementedError("Team not available")