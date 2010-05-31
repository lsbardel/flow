'''Implementation of jflow.core.finins.Root methods for fetching
portfolio data.
'''
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from jflow.core import finins
from jflow.core.dates import yyyymmdd2date
from jflow.conf import settings
from jflow.utils.encoding import smart_str
from jflow.db.trade.models import FundHolder, Fund, Position, ManualTrade



def team_portfolio_positions(dt = None, portfolio = None, team = None, logger = None):
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
    elif portfolio:
        if not isinstance(portfolio,Fund):
            try:
                portfolio = Fund.objects.get(code = settings.TRIM_STRING_CODE(portfolio))
            except ObjectDoesNotExist:
                logger.warning("portfolio %s not available" % portfolio)
                raise StopIteration
        positions = Position.objects.for_fund(dt = dt, fund = portfolio)
        trades = ManualTrade.objects.for_fund(team, dt = dt)
    else:
        positions = Position.objects.status_date_filter(dt = dt)
        trades = ManualTrade.objects.status_date_filter(dt = dt)
        
    for position in positions:
        yield position
    for trade in trades:
        yield trade


class Team(finins.Portfolio):
    pass


class FinRoot(finins.Root):
    '''Root class for financial instruments'''
    
    def _get(self, id):
        '''Get portfolio data from id'''
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
        if isinstance(obj,FundHolder):
            p = self.make_portfolio(obj.code, id, dt = dt, description = obj.description)
            data = team_portfolio_positions(logger = self.logger, team = obj, dt = dt)
            self._load_positions(p,data)
            return p
        elif isinstance(obj,Fund):
            p = self.make_portfolio(obj.code, id, dt = dt, description = obj.description)
            data = team_portfolio_positions(logger = self.logger, fund = obj, dt = dt)
            self._load_positions(p,data)
            return p
        else:
            pass
        
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
        return team_portfolio_positions(logger = self.logger, portfolio = portfolio.name, dt = portfolio.dt)
    
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
            
            
finins = FinRoot()