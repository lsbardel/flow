
from datetime import date, datetime

from stdnet import orm
from stdnet.contrib.timeserie.models import TimeSerieField


class FinInsBase(orm.StdModel):
    '''Base class for Financial Portfolio Models'''
    ccy     = orm.AtomField()
    
    
class FinIns(FinInsBase):
    '''Financial instrument base class                
    '''
    name   = orm.AtomField(unique = True)
    type   = orm.AtomField()
    data   = TimeSerieField()
        
    def __init__(self, multiplier = 1.0, description = '', **kwargs):
        self.multiplier    = multiplier
        self.description   = description
        super(FinIns,self).__init__(**kwargs)
        
    def pv01(self):
        '''Present value of a basis point. This is a Fixed Income notation which we try to extrapolate to
        all financial instruments'''
        return 0
    
    def price_to_value(self, price, size, dt):
        raise NotImplementedError("Cannot convert price and size to value")
    

class FinPositionBase(FinInsBase):
    name  = orm.AtomField()
    dt    = orm.DateField()
    
    def __init__(self, editable = False,
                 canaddto = False, movable = False, **kwargs):
        super(FinPositionBase,self).__init__(**kwargs)
        self.editable    = editable
        self.canaddto    = canaddto
        self.movable     = movable
        self.folder      = False
        
    def __repr__(self):
        return '%s:%s' % (self.name,self.dt)
    
    def __str__(self):
        return self.__repr__()
    
    def add_new_view(self, *args, **kwargs):
        raise NotImplementedError("Cannot add new view.")
    
    
class Portfolio(FinPositionBase):
    '''A portfolio containing positions and portfolios'''
    group      = orm.AtomField(required = False)
    user       = orm.AtomField(required = False)
    parent     = orm.ForeignKey('self', required = False, related_name = 'children')
    holder     = orm.ForeignKey('self', required = False, related_name = 'views')
    
    def __init__(self, **kwargs):
        super(Portfolio,self).__init__(**kwargs)
        self.folder   = True
    
    def root(self):
        if self.holder:
            return self.holder.root()
        elif self.parent:
            return self.parent.root()
        else:
            return self
        
    def addnewposition(self, inst, size, value):
        '''Add new position to portfolio holder'''
        if self.holder:
            raise ValueError("Cannot add position to portfolio view")
        pos = Position.objects.filter(portfolio = self, instrument = inst)
        if pos:
            raise ValueError('Cannot add position %s to portfolio. It is already available.' % instrument)
        p = Position(portfolio = self, size = size, value = value, ccy = inst.ccy,
                     name = inst.name, dt = self.dt, instrument = inst)
        return p.save()
    
    def add(self, item):
        if isinstance(item,Portfoilio):
            item.parent = self
            item.save()
    
    def _todict(self):
        d = super(Portfolio,self).todict()
        if self.instrument:
            d['description'] = self.instrument.description
        else:
            ps = []
            d['positions'] = ps
            for position in self.positions():
                ps.append(position.todict())
        return d
    
    def create_view(self, name, user = None):
        root = self.root()
        p = Portfolio(ccy = root.ccy,
                      name = name,
                      user = user,
                      group = root.group,
                      holder = root,
                      dt = root.dt)
        return p.save()
    
    def addNewFolder(self, name):
        '''Add folder for portfolio view. Self must have holder attribute available.'''
        if self.holder:
            folder = self.__class__(name = name, parent = self, ccy = self.ccy,
                                    holder = self.holder, user = self.user,
                                    group = self.group, dt = self.dt)
            return folder.save()
    

    
class Position(FinPositionBase):
    '''Financial position::
    
        * *sid* security id or None. For securities this is the underlying financial instrument id.
        * *size* size of position
        * *value* initial value of position
        * *dt* position date
    '''
    instrument = orm.ForeignKey(FinIns)
    portfolio  = orm.ForeignKey(Portfolio, related_name = 'positions')
    
    def __init__(self, size = 1, value = 0, **kwargs):
        self.size   = size
        self.value  = value
        super(Position,self).__init__(**kwargs)
        
    def todict(self):
        d = super(Position,self).todict()
        d['description'] = self.instrument.description
        return d
    

class PortfolioPosition(orm.StdModel):
    position  = orm.ForeignKey(Position)
    portfolio = orm.ForeignKey(Portfolio, related_name = 'portfolio_positions')
    
    
    
class UserViewDefault(orm.StdModel):
    user = orm.AtomField()
    view = orm.ForeignKey(Portfolio, related_name = 'user_default')

