from jflow.db.trade.models import Position
from jflow.core.finins import finins

from logger import log
from basejson import extract, listpop, positionBase
from marketrisk import MarketRiskPosition, MarketRiskPortfolio


POSITION_STATUS = 'all'


class MktPositionInterface(object):
    '''
    Interface for live and historical market positions
    '''
    def __new__(cls, *args, **kwargs):
        obj = super(MktPositionInterface, cls).__new__(cls)
        obj.isfund       = False
        obj.folder       = True
        obj.canaddto     = False
        obj.editable     = False
        obj.movable      = False
        obj.positionset  = None
        obj._fxcode      = None
        obj._fxcross     = 1.0
        obj._fxhistory   = None
        return obj
        
    def calc_ccy(self):
        return self.ccy
    
    def register_to_fxcross(self, cache):
        '''
        Obtain the exchange rate history
        '''
        c1 = self.ccy
        c2 = self.calc_ccy()
        if c1 != c2:
            self._fxcross  = 0.0
            fx = '%s%s' % (c1,c2)
            self._fxcode = fx
            try:
                h = cache.rates.get_data(fx, end = self.dte)
                h.addCallbacks(self.updatefx,self.errorfx)
            except Exception, e:
                self.err(e,'Failed to get FX rate %s' % fx)
            
    def updatefx(self, res):
        '''
        Got an update from historical forex rates
        '''
        try:
            dte, fx = res.back()
            self._fxhistory = res
            self._fxcross   = fx
            self.update()
            self.log('FX rate %s updated to %s' % (self._fxcode,fx), verbose = 3)
        except Exception, e:
            self.err(e,'FX rate %s update failed.' % self._fxcode)
        
    def errorfx(self, err):
        self.err(err,'Failed to retrive FX rate %s' % self._fxcode)


class jsonPosition(positionBase):
    '''
    An object mantaining all the information regarding a
    financial position.
    
    It holds an instance of jflow.core.finins.base.finins.finins
    a financial instrument object.
    
    '''
    def __init__(self, cache, fininst, position = None,
                 withinfo = False, register = True):
        '''
        Initialize a position object.
            @param cache:    the global cache object
            @param fininst:  instance of jflow.core.finins.base.finins.finins
            @param position: Optional a position object
            @param withinfo: Optional (default False)
            @param register: Optional (default False) if fill static information during construction
        '''
        obj = position or fininst.dbinstrument
        dte = fininst.calc_date
        super(jsonPosition,self).__init__(cache,obj,dte)
        self.__mkt_risk    = MarketRiskPosition(self.cache, self)
        self.fininst       = fininst
        self.size          = 0.0
        self.traded        = 0.0
        self.positions     = []
        if position:
            self.append(position, withinfo)
        if register:
            self.register()
        # register self with fininst for updates
        # IMPORTANT
        self.fininst.attach(self)
        # send an update to self. Just in case fininst is not receiving updates
        self.update()
    
    def _build(self):
        self._closebuild()
        
    def inthreadoverride(self, inthread):
        '''
        position is always run not on a separate thread
        '''
        return False
    
    def __get_ccy(self):
        return self.fininst.ccy()
    ccy = property(fget = __get_ccy)     
        
    def __get_calcdate(self):
        return self.fininst.calc_date
    calc_date = property(fget = __get_calcdate)
    
    def __get_ic(self):
        return self.dbinstrument.code
    ic = property(fget = __get_ic)
        
    def append(self, pos, withinfo = False):
        dt = self.dte.dateonly
        pv = pos.first_at_or_before(dt)
        try:
            sz = int(pv.size)
            self.size   += sz
            self.traded += float(pv.book_cost_base)
        except:
            #TODO Log this error
            sz = '#NA'
            log.err("Position %s has not history at %s" % (pos,dt))
        if withinfo:
            fund = pos.fund
            self.positions.append({'fund': fund.code,
                                   'name': fund.description,
                                   'size': sz})
        
    def notional(self):
        return float(self.fininst.dbinstrument.tonotional(self.size))
    
    def nav(self):
        return 0
    
    def allocation(self):
        return 0
    
    def refresh_me(self):
        super(jsonPosition,self).refresh_me()
        mr          = self.__mkt_risk
        fi          = self.fininst
        mr.notional = fi.notional(self.size)
        mr.nav      = fi.nav(self.size)
        mr.mktprice = fi.mktprice
        return mr
    
    def register2(self, code, jsv):
        return extract(self.fininst,code,jsv)
    
    def __get_mktrisk(self):
        self.refresh()
        return self.__mkt_risk
    mktrisk = property(fget = __get_mktrisk)


    
class jsonFund(positionBase):
    '''
    A Fund JSON object.
    This object mantains the information for a Fund object
    '''
    def __init__(self, cache, obj, dte):
        super(jsonFund,self).__init__(cache, obj, dte)
        self.element_objects = {}
        
    def positionsdict(self):
        r = {}
        r.update(self.element_objects)
        return r
        
    def _build(self):
        obj         = self.dbobj
        self.parent = obj.parent 
        dte         = self.dte
        funds       = obj.fund_set.all()
        elems       = self.element_objects
        self.funds  = []
        
        # Fund contains subfunds. Build the subfunds
        if funds:
            for f in funds:
                self.funds.append(self.cache.portfolio(f, dte))
            
            funds = self.funds[:]
            for f in funds:
                f.addcallback(self.addfund)
                
        # Fund has positions
        else:
            pos = Position.objects.positions_for_fund(fund = obj, dt = dte.dateonly, status = POSITION_STATUS)
            for p in pos:
                ic  = p.instrumentCode
                fi  = self.cache.instrument(ic, dte)
                if not fi:
                    continue
                jp  = jsonPosition(self.cache, fi, position = p)
                elems[jp.id] = jp
            self.log('Finished building')
            self._closebuild()
        
    def addfund(self, f):
        self.funds.remove(f)
        self.element_objects[f.id] = f
        if not self.funds:
            self.log('Finished building')
            self._closebuild()
    
    def _get_ccy(self):
        return self.dbobj.curncy
    ccy = property(fget = _get_ccy)
    


class jsonAggregatePosition(jsonPosition, MktPositionInterface):
    '''
    Aggregate position
    '''
    def __init__(self, cache, fininst, position, ccy, withinfo = True):
        jsonPosition.__init__(self, cache, fininst, position,
                                    withinfo = withinfo, register = False)
        self.convertccy    = ccy
        
    def __get_isposition(self):
        return self
    isposition = property(fget = __get_isposition)
    
    def register(self):
        if jsonPosition.register(self):
            self.register_to_fxcross(self.cache)
            return True
        else:
            return False
    
    def calc_ccy(self):
        return self.convertccy
    
    def refresh_me(self):
        mr = jsonPosition.refresh_me(self)
        json = self.json
        json['folder']   = self.folder
        json['canaddto'] = self.canaddto
        json['editable'] = self.editable
        json['movable']  = self.movable
        json['extra']    = self.positions
        mr.calculate()




class jsonTeam(positionBase):
    '''
    A Fund JSON object.
    This object mantains the information for a Team object
    '''
    def __init__(self, cache, obj, dte):
        super(jsonTeam,self).__init__(cache, obj, dte)
        self.parent           = None
        self.children         = [] 
        self.jelements        = []
        self.element_objects  = {}
        self.json['elements'] = self.jelements
        
    def _build(self):
        self.__mkt_risk = MarketRiskPortfolio(self.cache, self)
        dt     = self.dte.dateonly
        funds  = self.dbobj.fund_set.all()
        
        self.funds  = []
        
        # debugging
        #funds = funds[:1]
        
        # Create the funds
        for f in funds:
            self.funds.append(self.cache.portfolio(f,dt))
        
        # Add the callbacks
        funds = self.funds[:]
        for f in funds:
            f.addcallback(self.addfund)
    
    def addfund(self, f):
        self.funds.remove(f)
        elems   = self.element_objects
        jelems  = self.jelements
        
        for jpos in f.element_objects.values():
            if isinstance(jpos,jsonPosition):
                code = jpos.code
                aggp = elems.get(code,None)
                if not aggp:
                    aggp = jsonAggregatePosition(self.cache, jpos.fininst, jpos.dbobj, self.ccy)
                    # Register self as observer of aggp
                    aggp.attach(self)
                    elems[code] = aggp
                    self.children.append(code)
                    jelems.append(aggp.json)
                else:
                    aggp.append(jpos.dbobj, withinfo = True)
        
        # when finished, build the object
        if not self.funds:
            self.log('Finished adding funds')
            self.register()
            self._closebuild()
    
    def register(self):
        for jp in self.element_objects.values():
            jp.register()
        super(jsonTeam,self).register()
    
    def _get_ccy(self):
        return 'USD'
    ccy = property(fget = _get_ccy)
    
    def __get_mktrisk(self):
        mr  = self.__mkt_risk
        return mr
    mktrisk = property(fget = __get_mktrisk)
    
    def refresh_me(self):
        '''
        Called by observer superclass to refresh self values if needed
        '''
        #positionBase.refresh_me(self)
        self.__mkt_risk.calculate(withRisk = False)
