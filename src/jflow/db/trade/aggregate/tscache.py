'''
Cache objects
'''
import datetime
from threading import Lock

from jflow.core.timeseries import dateseries
from jflow.core.dates import get_livedate, now
from jflow.db.trade.models import Fund, FundHolder, PortfolioDisplayElement, Position, PortfolioView
from jflow.utils.tx import runInThread
from jflow.db.instdata.pricers import get_pricer
from jflow.rates import register_to_rates, get_rate, get_history

from position import jsonFund, jsonTeam
from portfoliotree import jsonPortfolioTree
from logger import PositionException

import basecache 


class CacheElement(basecache.cacheObject):
    '''
    Base class for time series cache elements
    '''
    def __init__(self, code, cache):
        super(CacheElement,self).__init__(cache)
        self.timestamp = now()
        self.ts        = dateseries()
        self.object    = self.get_object(code)
        self.__lock    = Lock()

    def __str__(self):
        return '%s - %s' % (self.__class__.__name__,self.object)
    
    def has_key(self, dt):
        return self.ts.has_key(dt)
    
    def get_object(self, code):
        return code
    
    def lastmodified(self):
        return datetime.datetime.min

    def get_or_create(self, dte, rjson, inthread = False):
        '''
        Create or return an element associated with date 'dte'
        dte      date
        rjson    boolean. If true a check on timestamp is performed
        '''
        dte = get_livedate(dte)
        dt  = dte.dateonly
        
        if rjson:
            lm  = self.lastmodified()
            if lm > self.timestamp:
                self.timestamp = now()
                self.ts        = dateseries()
        
        # thread safe creation
        self.__lock.acquire()
        try:
            if self.has_key(dt):
                return self.ts[dt]
            else:
                res = self.create(dte)
                if res:
                    self.ts[dt] = res
                self.build(res,inthread)
                return res
        except Exception, e:
            self.err(e)
            return None
        finally:
            self.__lock.release()
    
    def build(self, res, inthread):
        res.build(inthread)

    def create(self, dte):
        raise NotImplementedError
    
    def __get_display(self):
        return self.cache.display
    display = property(fget = __get_display)
    


class InstrumentTs(CacheElement):
    '''
    Risk and value calculator for a financial instrument.
    This is the building block of market and risk calculation.
    '''
    def __init__(self, *args):
        super(InstrumentTs,self).__init__(*args)
        self.rates = {}  
        
    def create(self, dte):
        '''
        Create a new instrument and register with market data for
        portfolio calculations
        '''
        try:
            inst = self.object.instrument()
            fin  = inst.make_position(calc_date = dte)
            if fin == None:
                self.err('Instrument %s does not have an implementation for calculation' % inst)
            return fin
        except Exception, e:
            self.err(e)
        
    def build(self, fin, inthread):
        # Set the pricer
        if not fin:
            return
        try:
            fin.pricer = get_pricer(fin.type)
            if fin.pricer:
                fin.pricer.logger = self
                dte = fin.calc_date
                fin.pricer.loadhistory(fin, self.cache.rates.get_data, end = dte)
            else:
                self.err('Pricer not available for %s' % fin)
        except Exception, e:
            self.err(e)
    
    def errback(self, res):
        self.err("Error in history request")


class PortfolioTs(CacheElement):
    '''
    Portfolio cache.
    This cache object contain a timeserie for a given fund
    '''
    def __init__(self, *args):
        super(PortfolioTs,self).__init__(*args)
        
    def get_object(self, code):
        if isinstance(code,Fund):
            return code
        else:
            return Fund.objects.get(code = code)
    
    def create(self, dte):
        self.log("fetching at %s" % dte)
        #return jsonFund(self.cache,self.object,dte,self.object.curncy)
        return jsonFund(self.cache,self.object,dte)
    
    @runInThread
    def set_pricer(self, jportfolio,pricer):
        for p in jportfolio.plist:
            p.set_pricer(pricer)
            
            
class PortfolioViewTs(CacheElement):
    '''
    Portfolio view cache
    '''
    def __init__(self, *args):
        super(PortfolioViewTs,self).__init__(*args)
        
    def get_object(self, code):
        return PortfolioView.objects.get(id = code)
    
    def lastmodified(self):
        return PortfolioView.objects.get_last_modified()
    
    def create(self, dte):
        self.log("fetching at %s" % dte)
        return jsonPortfolioTree(self.cache,self.object,dte)
    
    @runInThread
    def set_pricer(self, jportfolio,pricer):
        for p in jportfolio.plist:
            p.set_pricer(pricer)
            
            
class AggregateTs(CacheElement):
    '''
    Position aggregator.
    This cache element aggregate position across all funds of a given team
    '''
    def __init__(self, *args):
        super(AggregateTs,self).__init__(*args)
        
    def get_object(self, code):
        return FundHolder.objects.get(code = code)
            
    def create(self, dte):
        self.log("aggregating at %s" % dte)
        return jsonTeam(self.cache,self.object,dte)
    
        
    