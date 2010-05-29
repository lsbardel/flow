
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
    
    InstrumentFactory = {'equity':equity,
                         'etf':etf}
    
    def _load_positions(self, portfolio, gendata):
        '''Given a portfolio instance and a generator of data, load the portfolio positions:
        
            * *portfolio* Porfolio instance
            * *gendata* iterable on positions
        '''
        skey    = portfolio.setkey()
        cache.delete(skey)
        dt      = portfolio.dt
        pids    = []
        for position in gendata:
            pid = self.get_object_id(position)
            p   = cache.get(pid)
            if not p:
                p = self.create_position(pid, position)
                if p:
                    cache.set(p.id,p)
            if p:
                pids.append(p.id)
        N = cache.sadd(skey,pids)
        self.logger.debug("added %s positions to portfolio %s" % (N,portfolio))
        return N
        
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
    
    def create_position(self, pid, position):
        '''create a finins position'''
        sid,name,obj = self.get_instrument_id_from_position(position)
        if not sid:
            return
        
        fi  = cache.get(sid)
        if not fi:
            factory  = self.InstrumentFactory.get(name,None)
            if not factory:
                return
            fi = factory(id = sid, **self.instobjmapper(obj))
            if fi:
                cache.set(fi.id,fi)
                return Position(sid   = fi.id,
                                id    = pid,
                                ccy   = fi.ccy,
                                name  = fi.name,
                                size  = position.size,
                                value = position.value,
                                dt    = position.dt) 
    
    def instobjmapper(self, obj):
        raise NotImplementedError('Cannot obtain instrument information form %s' % obj)
    
    def positions(self, portfolio):
        raise NotImplementedError('cannot obtain positions for portfolio %s' % portfolio)
    
    def get_instrument_id_from_position(self, position):
        raise NotImplementedError('Cannot obtain instrument id and name from position')
    
    def get_team_data(self, team, date):
        raise NotImplementedError('This function needs to be implemented by derived class')
    

    
