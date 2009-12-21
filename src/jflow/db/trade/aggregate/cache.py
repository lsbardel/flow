from django.contrib.contenttypes.models import ContentType

from jflow.core.dates import now
from jflow.core.pricers import Pricer
from jflow.db.trade.models import Position, PortfolioDisplayElement, PortfolioDisplay
#from jflow.db.trade.portfolio import get_liveposition, get_port_id
from jflow.db import geo
from jflow.utils.observer import lazyobject
from jflow.utils.baseval import baseval
from jflow.utils.tx import runInThread

from basecache import cacheBase
from tscache import InstrumentTs, PortfolioTs, PortfolioViewTs, AggregateTs
from rates import PortfolioRates



def get_cache():
    global _pcache
    return _pcache

        

def cachewrap(f):
    '''
    Decorator for cache methods.
    This decorator check if rjson is set to true in the argument list.
    If it is, it serialize the object into a JSON string
    '''
    def wrapper(self, *args, **kwargs):
        # Check if positions have changed
        self.timecheck()
        el = f(self, *args,**kwargs)
        rjson = kwargs.get('rjson',False)
        if el == None:
            return None
        
        # a serialization has been requested
        if rjson:
            if el.building:
                # The object is building. Return a JSON message saying so
                return el.jsonDescription("Calculation is under way. Call back in few minutes");
            else:
                return el.rjson()
        else:
            return el
    
    return wrapper



class CalculationCache(cacheBase):
    '''
    Cache object for calculating portfolio analytics
    '''
    def __init__(self):
        super(CalculationCache,self).__init__()
        self.lastaccess = None
        self.rates      = PortfolioRates(self)
        self.flush()
        
    def __str__(self):
        return '%s' % self.__class__.__name__
        
    def timecheck(self):
        lm = Position.get_last_modified()
        ld = PortfolioDisplay.objects.get_last_modified()
        la = self.lastaccess
        if la:
            if lm > la or ld > la:
                self.flush()
        self.lastaccess = now()

    @cachewrap
    def portfolio(self, code, dte, rjson = False, inthread = True):
        return self.__make(code, dte, PortfolioTs, self.__portfolios, rjson, inthread)
    
    @cachewrap
    def portfolioview(self, code, dte, rjson = False, inthread = True):
        return self.__make(code, dte, PortfolioViewTs, self.__portfolioviews, rjson, inthread)
    
    @cachewrap
    def aggregates(self, code, dte, rjson = False, inthread = True):
        return self.__make(code, dte, AggregateTs, self.__team_aggregates, rjson, inthread)
    
    @cachewrap
    def instrument(self, code, dte, rjson = False):
        return self.__make(code, dte, InstrumentTs, self.__instruments, rjson)
    
    @cachewrap
    def addfolder(self, viewid, dte, code, parentid, rjson = False):
        p = self.portfolioview(viewid, dte)
        return p.addfolder(code,parentid)
    
    @cachewrap
    def editfolder(self, viewid, dte, data, rjson = False):
        p = self.portfolioview(viewid, dte)
        return p.editfolder(data)
    
    @cachewrap
    def removePortfolioNode(self, viewid, dte, id, rjson = False):
        p = self.portfolioview(viewid, dte)
        return p.pop(id)
    
    @cachewrap
    def movePortfolioNode(self, viewid, dte, id, target, rjson = False):
        p = self.portfolioview(viewid, dte)
        return p.move(id,target)
    
    @cachewrap
    def marketRisk(self, viewid, dte, id, rjson = False):
        p = self.portfolioview(viewid, dte)
        return p.marketRisk(id)
                
    def flush(self, code = None):
        self.log("Flushing")
        self.__team_aggregates = {}
        self.__portfolioviews  = {}
        self.__portfolios      = {}
        self.__instruments     = {}
        self.display           = list(PortfolioDisplayElement.objects.all())
        self.displaydict       = {}
        p = 0
        for d in self.display:
            self.displaydict[d.code] = p
            p += 1
        
    def __make(self, code, dte, object, holder, rjson, inthread = False):
        '''
        Create the new JSON object
            @param code: code used to retrive the databse object
            @param dte:  date for calculation
            @param object: JSON class to be built   
        '''
        scode = str(code)        
        pts = holder.get(scode,None)
        if pts == None:
            pts = object(code,self)
            holder[scode] = pts
        return pts.get_or_create(dte, rjson, inthread)
    
    def get_object_id(self, obj):
        '''
        Given an object instance it return a unique id across all models
        '''
        opt = obj._meta
        ct = ContentType.objects.get_for_model(obj)
        return '%s_%s' % (ct.id,obj.id)

    def get_object_from_id(id):
        try:
            ids = str(id).split('_')
            ct = ContentType.objects.get_for_id(int(ids[0]))
            return ct.get_object_for_this_type(id = int(ids[1]))
        except:
            return None
        
        

_pcache = CalculationCache()

