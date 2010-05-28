
#from instruments import *
#from base import *
#from equity import *
#from fx import *
from future import *
#from fi import *
#from cash import *
from portfolio import *
from equity import *
from formatter import *

from jflow.log import LoggingClass
from jflow.core.dates import date2yyyymmdd


class Root(LoggingClass):
    
    def __init__(self):
        from jflow.conf import settings
    
    def positions(self, portfolio):
        raise NotImplementedError
    
    def _positions(self, portfolio, gendata):
        '''Given a portfolio instance and a generator of data, build the portfolio positions:
        
            * *portfolio* Porfolio instance
            * *gendata* iterable on positions
        '''
        skey    = portfolio.setkey()
        cache.delete(skey)
        dt      = portfolio.dt
        pids    = []
        for position in gendata:
            id = self.get_object_id(position)
            p = cache.get(id)
            if not p:
                p = self.create_position(id, position)
                if p:
                    cache.set(p.id,p)
            if p:
                pids.append(p.id)
        cache.sadd(skey,pids)
        self.logger.debug("added %s positions to portfolio %s" % (len(pids),portfolio))
        
    def get_portfolio(self, name, dt = None):
        '''For a given portfolio name returns a portfolio instance
        
            * **name** string code defining the team
            * *dt* date of calculation
        '''
        p = Portfolio(name = name , dt = dt)
        namekey = p.namekey()
        po = cache.get(namekey)
        if po:
            return po
        else:
            self.positions(p)
            cache.set(namekey,p)
        return p
    
    def get_object_id(self, obj):
        '''Given an instance *obj* return a unique ID used for storing the object in the
        poorfolio cache'''
        raise NotImplementedError
    
    def get_team_data(self, team, date):
        raise NotImplementedError('This function needs to be implemented by derived class')
    

    
