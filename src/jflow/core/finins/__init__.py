from stdnet.main import get_cache

#from instruments import *
#from base import *
#from equity import *
#from fx import *
from future import *
#from fi import *
#from cash import *
from portfolio import *
from formatter import *

from jflow.log import LoggingClass
from jflow.core.dates import date2yyyymmdd


class Root(LoggingClass):
    
    def __init__(self):
        from jflow.conf import settings
        self.cache = get_cache(settings.PORTFOLIO_CACHE_BACKEND or settings.CACHE_BACKEND)
    
    def get_portfolio(self, name, dt = None):
        '''For a given portfolio name returns a portfolio instance
        
            * **name** string code defining the team
            * *dt* date of calculation
        '''
        return Portfolio(name = name , dt = dt, root = self)
    
    def positions(self, portfolio):
        raise NotImplementedError
                
    def get_team_data(self, team, date):
        raise NotImplementedError('This function needs to be implemented by derived class')
    

