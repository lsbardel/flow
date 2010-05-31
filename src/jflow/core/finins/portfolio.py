import time
from datetime import date, datetime

from stdnet.main import get_cache
from stdnet.utils import json

from jflow.conf import settings
from jflow.core.dates import date2yyyymmdd

__all__ = ['cache','FinInsBase','Portfolio','FinIns','Position']


cache = get_cache(settings.PORTFOLIO_CACHE_BACKEND or settings.CACHE_BACKEND)

rdate = lambda d: time.mktime(d.timetuple())

class JSONRPCEncoder(json.JSONEncoder):
    """
    Provide custom serializers for JSON-RPC.
    """
    def default(self, obj):
        if isinstance(obj, date) or isinstance(obj, datetime):
            return rdate(obj)
        else:
            raise exceptions.JSONEncodeException("%r is not JSON serializable" % (obj,))


class FinInsBase(object):
    notavailable  = '#N/A'
    
    def __init__(self, id = None, name = '', description = '', ccy = None):
        self.id = str(id)
        self.name = str(name)
        self.description = str(description)
        self.ccy = str(ccy).upper()
        
    def __repr__(self):
        return self.name
    
    def __str__(self):
        return self.__repr__()
    
    def has_id(self, id):
        return False
    
    def prekey(self):
        return '%s:%s' % (self.__class__.__name__.lower(),date2yyyymmdd(self.dt))
        
    def key(self):
        return '%s:#%s' % (self.prekey(),self.id)
    
    def namekey(self):
        return '%s:$%s' % (self.prekey(),self.name)
    
    def todict(self):
        d = self.__dict__.copy()
        return d
    
    def tojson(self):
        return json.dumps(self.todict(), cls = JSONRPCEncoder)
    

class FinDated(FinInsBase):
    
    def __init__(self, dt = None, **kwargs):
        self.dt = dt or date.today()
        super(FinDated,self).__init__(**kwargs)
        
    def __repr__(self):
        return '%s:%s' % (self.name,self.dt)


class Portfolio(FinDated):
    '''A portfolio containing positions and portfolios'''
    
    def get(self, id, default = None):
        code = '%s:position:$%s' % (self.key(),id)
        return cache.get(code.lower(),default)
    
    def setkey(self):
        return '%s:positions' % self.namekey()
    
    def positions(self):
        '''Portfolio positions'''
        pids = cache.sinter(self.setkey())
        for pid in pids:
            p = cache.get(pid)
            yield p
            
    def add(self, item):
        if isinstance(item,PositionBase):
            cal
            if self.has_key(c):
                raise KeyError, '%s already available in %s' % (c,self)
            else:
                self._positions[c] = item
                return item
        else:
            return None
    
    def get_portfolio(self):
        pos = []
        for v in self._positions.itervalues():
            pos.append(v.dict())
        return pos
    
    def todict(self):
        d = super(Portfolio,self).todict()
        ps = []
        d['positions'] = ps
        for position in self.positions():
            ps.append(position.todict())
        return d
    
    
class FinIns(FinInsBase):
    '''Financial instrument base class                
    '''    
    def __init__(self, multiplier = 1.0, **kwargs):
        self.multiplier    = multiplier
        super(FinIns,self).__init__(**kwargs)
        
    def pv01(self):
        '''Present value of a basis point. This is a Fixed Income notation which we try to extrapolate to
        all financial instruments'''
        return 0
    
    def price_to_value(self, price, size, dt):
        raise NotImplementedError("Cannot convert price and size to value")
 
 
class Position(FinDated):
    '''Financial position::
    
        * *sid* security id or None. For securities this is the underlying financial instrument id.
        * *size* size of position
        * *value* initial value of position
        * *dt* position date
    '''
    def __init__(self, sid = None, size = 1, value = 0, **kwargs):
        self.sid    = sid
        self.size   = size
        self.value  = value
        super(Position,self).__init__(**kwargs)

    def security(self):
        if self.sid:
            return cache.get(self.sid)
    
    