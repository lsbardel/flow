
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
from fields import *

from jflow.log import LoggingClass
from jflow.core.dates import date2yyyymmdd



class portfolio_generator(object):
    
    def __init__(self):
        '''Utility class for generating portfolios
        '''
        pass




class Root(LoggingClass):
    keyprefix = 'jflow-finins'
    
    InstrumentFactory = {'equity':equity,
                         'etf':etf}
    
    make_portfolio = Portfolio
    
    #__________________________________________________ API
    def get(self, id):
        '''Obtain portfolio or instrument from id. It check cache first, otherwise build and cache it.
        Returns an instance of :ref:`FinInsBase` or None'''
        el = cache.get(id)
        if not el:
            el = self._get(id)
            if el:
                cache.set(el.id,el)
        return el
    
    def get_portfolio(self, name, dt = None):
        '''For a given portfolio name returns a portfolio instance
        
            * **name** string code defining the portfolio
            * *dt* date of calculation
        '''
        p = Portfolio(name = name , dt = dt)
        namekey = p.namekey()
        po = cache.get(namekey)
        if po:
            return po
        else:
            data = self._positions(p)
            self._load_positions(p, data)
            cache.set(namekey,p)
        return p
    
    def get_object_id(self, obj, dt = None):
        '''Generate a unique id from object and date'''
        id = '%s:%s' % (self.keyprefix,self._get_object_id(obj))
        if dt:
           id = '%s:%s' % (id,date2yyyymmdd(dt))
        return id
    
    def fields(self):
        return finfields
    
    #___________________________________________________ IMPLEMENTATION
    
    def _get(self, id, dt = None):
        '''Obtain portfolio or instrument from id and date'''
        raise NotImplementedError('Cannot obtain data for %s.' % id)
    
    def _get_object_id(self, obj):
        '''Given an instance *obj* return a unique ID used for storing the object in the
        poorfolio cache'''
        raise NotImplementedError('Cannot obtain id for %s' % obj)
    
    def instobjmapper(self, obj):
        '''Given an object *obj* return a dictionary containing information about the object'''
        raise NotImplementedError('Cannot obtain instrument information form %s' % obj)
    
    def _positions(self, portfolio):
        '''Given an instance *portfolio* of Portfolio obtain information about subportfolios and positions'''
        raise NotImplementedError('Cannot obtain positions for portfolio %s' % portfolio)
    
    def get_instrument_id_from_position(self, position):
        raise NotImplementedError('Cannot obtain instrument id and name from position.')
    
    def _get_position_value(self, position, fi):
        '''return a 2-elements tuple defining the position value and size'''
        return position.value, position.size
    
    def _load_positions(self, portfolio, gendata):
        '''Given a portfolio instance and a generator of data, load the portfolio positions:
        
            * *portfolio* Porfolio instance
            * *gendata* iterable on positions/subportfolios
        '''
        skey    = portfolio.setkey()
        cache.delete(skey)
        dt      = portfolio.dt
        pids    = []
        for position in gendata:
            pid = self.get_object_id(position,dt)
            p   = cache.get(pid)
            if not p:
                p = self._create_position(portfolio, pid, position)
                if p:
                    cache.set(p.id,p)
            if p:
                pids.append(p.id)
        N = cache.sadd(skey,pids)
        self.logger.debug("added %s positions to portfolio %s" % (N,portfolio))
        return N
    
    def _create_position(self, portfolio, pid, position):
        '''create a finins position for *portfolio*'''
        sid,name,obj = self.get_instrument_id_from_position(position)
        if not sid:
            return
        
        dt  = portfolio.dt
        fi  = cache.get(sid)
        if not fi:
            factory  = self.InstrumentFactory.get(name,None)
            if not factory:
                return
            fi = factory(id = sid, **self.instobjmapper(obj))
            if fi:
                cache.set(fi.id,fi)
                value, size = self._get_position_value(position,fi,dt)
                return Position(sid   = fi.id,
                                id    = pid,
                                ccy   = fi.ccy,
                                name  = fi.name,
                                size  = size,
                                value = value,
                                dt    = dt) 
    

    
