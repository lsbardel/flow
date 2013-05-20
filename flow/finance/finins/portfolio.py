from datetime import date, datetime
from stdnet import orm
from stdnet.contrib.timeserie.models import TimeSerieField

from jflow.conf import settings

__all__ = ['FinInsBase','Portfolio','FinIns','Position']


class FinInsBase(orm.StdModel):
    '''Base class for Financial Model'''
    ccy     = orm.AtomField()
    
    
class FinIns(FinInsBase):
    '''Financial instrument base class                
    '''
    name = orm.AtomField(unique = True)
    data = TimeSerieField()
        
    def __init__(self, multiplier = 1.0, **kwargs):
        self.multiplier    = multiplier
        super(FinIns,self).__init__(**kwargs)
        
    def pv01(self):
        '''Present value of a basis point. This is a Fixed Income notation which we try to extrapolate to
        all financial instruments'''
        return 0
    
    def price_to_value(self, price, size, dt):
        raise NotImplementedError("Cannot convert price and size to value")

    

class FinPositionBase(FinInsBase):
    name = orm.AtomField()
    dt   = orm.DateField()
    
    def __init__(self, description = '', editable = False,
                 canaddto = False, movable = False,
                 group = None, user = None, **kwargs):
        self.description = str(description)
        self.editable    = editable
        self.canaddto    = canaddto
        self.movable     = movable
        self.folder      = False
        self.group       = group
        self.user        = user
        
    def __repr__(self):
        return '%s:%s' % (self.name,self.dt)
    
    def __str__(self):
        return self.__repr__()
    
    def add_new_view(self, *args, **kwargs):
        raise NotImplementedError("Cannot add new view.")
    
    
class Position(FinPositionBase):
    '''Financial position::
    
        * *sid* security id or None. For securities this is the underlying financial instrument id.
        * *size* size of position
        * *value* initial value of position
        * *dt* position date
    '''
    instrument = orm.ForeignKey(FinIns)
    
    def __init__(self, size = 1, value = 0, **kwargs):
        self.size   = size
        self.value  = value
        super(Position,self).__init__(**kwargs)
        
    def todict(self):
        d = super(Position,self).todict()
        d['description'] = self.instrument.description
        return d

    
class Portfolio(FinPositionBase):
    '''A portfolio containing positions and portfolios'''
    team     = orm.AtomField(required = False)
    parent   = orm.ForeignKey('self', required = False, related_name = 'children')
    holder   = orm.ForeignKey('self', required = False, related_name = 'views')
    position = orm.ForeignKey(Position, required = False, related_name = 'views')
    
    def __init__(self, **kwargs):
        super(Portfolio,self).__init__(**kwargs)
        self.folder   = True
    
    def setkey(self):
        return '%s:positions' % self.key()
    
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
