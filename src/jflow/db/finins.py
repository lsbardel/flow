'''Implementation of jflow.core.finins.Root methods for fetching
portfolio data.
'''
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from jflow.core import finins
from jflow.core.dates import yyyymmdd2date
from jflow.conf import settings
from jflow.utils.encoding import smart_str
from jflow.utils.anyjson import json
from jflow.db.trade.models import FundHolder, Fund, Position, ManualTrade, UserViewDefault
from jflow.db.trade.models import PortfolioView, PortfolioDisplay


class portfolio_view(finins.Portfolio):
    
    def __init__(self, fund_id, **kwargs):
        self.fund_id = fund_id
        super(portfolio_view,self).__init__(**kwargs)
        
    def get_data(self, obj):
        '''Build portfolio view data from database
        '''
        pass


def get_object_from_id(id):
    ids = id.split(':')
    obj = None
    dt  = None
    N   = len(ids)
    if N == 4:
        dt = yyyymmdd2date(int(ids[-1]))

    if N >= 3:
        try:
            ct = ContentType.objects.get_for_id(int(ids[1]))
            obj = ct.get_object_for_this_type(id = int(ids[2]))
        except:
            pass
    return obj,dt


def default_view(fund, user):
    root = fund.root()
    if user.is_authenticated():
        view = UserViewDefault.objects.filter(user = user, view__fund = root)
        if view:
            return view[0]
    views = PortfolioView.objects.filter(fund = root)
    if not views:
        view = PortfolioView(fund = fund, default = True, name = 'default')
        view.save()
        return view
    else:
        if user.is_authenticated():
            uviews = views.filter(user = user)
            if uviews:
                return uview[0]
        uviews = views.filter(default = True)
        if uviews:
            return uviews[0]
        else:
            return views[0]
    

def team_portfolio_positions(dt = None, fund = None, team = None, logger = None):
    '''Generator of positions for a given date'''
    if team:
        if not isinstance(team,FundHolder):
            try:
                team = FundHolder.objects.get(code = settings.TRIM_STRING_CODE(team))
            except:
                self.logger.warning("team %s not available" % team)
                raise StopIteration
        positions = Position.objects.for_team(dt = dt, team = team)
        trades = ManualTrade.objects.for_team(team, dt = dt)
    elif fund:
        if not isinstance(fund,Fund):
            try:
                fund = Fund.objects.get(code = settings.TRIM_STRING_CODE(fund))
            except ObjectDoesNotExist:
                logger.warning("portfolio %s not available" % fund)
                raise StopIteration
        positions = Position.objects.for_fund(dt = dt, fund = fund)
        trades = ManualTrade.objects.for_fund(team, dt = dt)
    else:
        positions = Position.objects.status_date_filter(dt = dt)
        trades = ManualTrade.objects.status_date_filter(dt = dt)
        
    for position in positions:
        yield position
    for trade in trades:
        yield trade




class FinRoot(finins.Root):
    '''Root class for financial instruments'''
    
    def _get(self, id):
        '''Create portfolio data from id'''
        obj,dt = get_object_from_id(id)
        
        if isinstance(obj,FundHolder):
            p = self.make_portfolio(obj.code, id, dt = dt, description = obj.description)
            data = team_portfolio_positions(logger = self.logger, team = obj, dt = dt)
            self._load_positions(p,data)
            return p
        elif isinstance(obj,Fund):
            if obj.parent:
                p = self.make_portfolio(name = obj.code,
                                        id = id,
                                        dt = dt,
                                        description = obj.description,
                                        canaddto = not obj.children.count(),
                                        ccy = obj.curncy)
            data = team_portfolio_positions(logger = self.logger, fund = obj, dt = dt)
            self._load_positions(p,data)
            return p
        
        if isinstance(obj,PortfolioView):
            fund = obj.fund
            fid  = self.get_object_id(fund,dt)
            ff   = self.get(fid)
            p    = portfolio_view(name = fund.code,
                                  fund_id = fid,
                                  id = id,
                                  dt = dt,
                                  description = obj.description)
            data = p.get_data(obj)
            self._load_positions(p,data)
            return p
        
    def _get_position_value(self, position, fi, dt):
        '''Return value and size of position'''
        size = float(str(position.size))
        if isinstance(position,Position):
            return position.value, size
        else:
            return fi.price_to_value(position.price,size,dt), size
    
    def _positions(self, portfolio):
        '''Generator of positions.
        Implements virtual method from parent class by obtaining
        data from the database.'''
        return team_portfolio_positions(logger = self.logger, fund = portfolio.name, dt = portfolio.dt)
    
    def funds(self, team):
        '''Aggregate fund for a given team'''
        data = team_portfolio_positions(logger = self.logger, portfolio = portfolio.name, dt = portfolio.dt)
        
    def _get_object_id(self, obj):
        '''Given an object instance it return a unique id across all models
        '''
        opt = obj._meta
        ct = ContentType.objects.get_for_model(obj)
        return '%s:%s' % (ct.id,obj.id)
        
    def get_instrument_id_from_position(self, position):
        dataid = position.dataid
        inst   = dataid.instrument
        if not inst:
            return None,None,None
        return self.get_object_id(dataid),inst._meta.module_name,dataid
    
    def instobjmapper(self, obj):
        return {'name': obj.code,
                'description': obj.name,
                'ccy': obj.curncy}
    
    
    def get_team(self, team, dt = None):
        '''For a given team and date aggregate all portfolios
        
            * **name** string code defining the team
            * **date** date of calculation
        '''
        if not isinstance(team,FundHolder):
            team = FundHolder.objects.get(name = team)
        tobj = Team(name = team.code, dt = dt)
        agg  = cache.get(tobj.namekey())
        if agg:
            return self.loads(agg)
        
        # Gather all positions from database
        data = team_portfolio_positions(team = team, dt = dt)            
        agg = self._build_team_aggregate(key, team, date, data)
        cache.set(key,agg)
        return agg
    
    def get_portfolio_positions(self, nameid = None, dt = None):
        '''Fetch portfolio positions for a given date'''
        data = team_portfolio_positions(portfolio = nameid, dt = dt)
        for position in data:
            id = get_object_id(position)
            p = self.get_position(id)
            if not p:
                p = create(id, position)
                self.set_position(p.id,p)
            if p:
                yield p
            
    # SPECIFIC APPLICATION___________________________________________________________________________
    
    def view_for_funds(self, fund, dt, user):
        '''List of fund views for a given date with user information'''
        dviews = []
        views = fund.views.all()
        default = None
        if not views:
            view = PortfolioView(fund = fund,
                                 name = "default")
            view.save()
            default = view
            
        for view in fund.views.all():
            dviews.append({'id': self.get_object_id(view,dt),
                           'name': obj.name,
                           'description': view.description,
                           'editable': view.user is user})

        return dviews
    
    def update_view(self, view, dt):
        '''Update a portfolio view according to a predifined algorithm:
        
            * *view* instance of PortfolioView
            * *dt* date
        '''
        pass
    
    def get_display_object(self, instance, user):
        if isinstance(instance,Fund):
            return default_view(instance,user)
        else:
            return instance


    def do_action(self, request, action, id, data):
        func = getattr(self,'action_%s' % action.replace('-','_'))
        if func:
            return func(request, id, data)
        else:
            return ''
        
    # ------------------------------------------------------------ JSON API ACTIONS
    
    def action_load(self, request, id, data):
        '''Load portfolio from id. Returns a json string'''
        fi = self.get(id)
        return fi.tojson()
    
    def action_display(self, request, id, data):
        return json.dumps(PortfolioDisplay.objects.dict_user(request.user))
        
    def action_add_edit_node(self, request, id, data):
        '''Add or edit a portfolio'''
        fi = finins.get(id)
        if data.pop("editing",False):
            fi.edit(data)
            return fi.tojson()
        elif fi.canaddto:
            obj,dt = get_object_from_id(id)
            name   = data.get('name',None)
            description = data.get('description','')
            if not name:
                return
            
            
            
            
            
            
finins = FinRoot()
    
    
