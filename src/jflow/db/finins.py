from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from jflow.core import finins
from jflow.conf import settings
from jflow.utils.encoding import smart_str
from jflow.db.trade.models import FundHolder, Fund, Position


def create(id, position):
    '''create a finins instance'''
    dataid = position.dataid
    inst   = dataid.instrument
    if not inst:
        return None
    
    
def get_object_id(obj):
    '''
    Given an object instance it return a unique id across all models
    '''
    opt = obj._meta
    ct = ContentType.objects.get_for_model(obj)
    return '%s:%s' % (ct.id,obj.id)


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
        trades = Position.objects.for_team(dt = dt, team = team)
    elif portfolio:
        if not isinstance(portfolio,Fund):
            try:
                portfolio = Fund.objects.get(code = settings.TRIM_STRING_CODE(portfolio))
            except ObjectDoesNotExist:
                logger.warning("portfolio %s not available" % portfolio)
                raise StopIteration
        positions = Position.objects.for_fund(dt = dt, fund = portfolio)
    else:
        positions = Position.objects.status_date_filter(dt = dt)
            
    for position in positions:
        id = get_object_id(position)
        p = self.get_position(id)
        if not p:
            p = create(id, position)
            self.set_position(p.id,p)
        if p:
            yield p


class Team(finins.Portfolio):
    pass


class FinRoot(finins.Root):
    '''Root class for financial instruments'''
    
    def positions(self, portfolio):
        '''Generator of positions.
        Implements virtual method from parent class by obtaining
        data from the database.'''
        data = team_portfolio_positions(logger = self.logger, portfolio = portfolio.name, dt = portfolio.dt)
        for position in data:
            id = get_object_id(position)
            p = self.get_position(id)
            if not p:
                p = create(id, position)
                self.set_position(p.id,p)
            if p:
                yield p
            
    
    def get_team(self, name, dt):
        '''For a given team and date aggregate all portfolios
        
            * **name** string code defining the team
            * **date** date of calculation
        '''
        tobj = Team(name = name, dt = dt)
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
            