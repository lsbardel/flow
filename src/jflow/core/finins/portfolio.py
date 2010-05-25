import datetime

from jflow.core.dates import date2yyyymmdd

__all__ = ['FinInsBase','Portfolio','FinIns']


class FinInsBase(object):
    
    def __init__(self, id = None, name = None, dt = None, root = None):
        self.id = id
        self.name = name
        self.dt = dt or datetime.date.today()
        self.root = root
        
    def __repr__(self):
        return '%s:%s' % (self.name,self.dt)
    
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
        return {'id': self.id,
                'name': self.name}
    

class Portfolio(FinInsBase):
    '''A portfolio containing positions and portfolios'''
    
    def get(self, id, default = None):
        code = '%s:position:$%s' % (self.key(),id)
        return cache.get(code.lower(),default)
    
    def positions(self):
        return self.root.positions(self)
            
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
    
    
class FinIns(FinInsBase):
    pass
        