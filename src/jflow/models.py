
from datetime import date, datetime

from stdnet import orm
from stdnet.contrib.timeserie.models import TimeSerieField

__all__ = ['FinIns',
           'PortfolioHolder',
           'Portfolio',
           'Position',
           'PortfolioView',
           'PortfolioViewFolder',
           'UserViewDefault']


class FinIns(orm.StdModel):
    '''Financial instrument base class. Contains a time-serie field.                
    '''
    name   = orm.AtomField(unique = True)
    ccy    = orm.AtomField()
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
    
    
class PortfolioHolder(orm.StdModel):
    name       = orm.AtomField(unique = True)
    group      = orm.AtomField()
    ccy        = orm.AtomField()
    parent     = orm.ForeignKey('self',
                                required = False,
                                related_name = 'children')
    
    def __init__(self, description = '', **kwargs):
        super(PortfolioHolder,self).__init__(**kwargs)
        self.description = description
        
    def __str__(self):
        return self.name
    
    def root(self):
        '''Return Root Portfolio'''
        if self.parent:
            return self.parent.root()
        else:
            return self
    

class FinPositionBase(orm.StdModel):
    editable = False
    canaddto = False
    movable  = False
    folder   = True
    
    class Meta:
        abstract = True
    
    def get_tree(self):
        return None
    
    def alldata(self):
        d = self.todict()
        d['tree'] = self.get_tree()
        return d
    
    
class Portfolio(FinPositionBase):
    '''A portfolio containing positions and portfolios'''
    holder     = orm.ForeignKey(PortfolioHolder, related_name = 'dates')
    dt         = orm.DateField()
    
    def __str__(self):
        return '%s: %s' % (self.holder,self.dt)
    
    def root(self):
        '''Return Root Portfolio'''
        root = self.holder.root()
        if root == self.holder:
            return self
        else:
            raise NotImplementedError
        
    def children(self):
        children = self.holder.children.all()
        if children:
            for child in children:
                raise NotImplementedError
        else:
            return None
        
    def customAttribute(self, name):
        return getattr(self.holder,name)
        
    def addnewposition(self, inst, size, value):
        '''Add new position to portfolio:
 * *inst* FinIns instance
 * *size* position size
 * *value* position value

*inst* must not be in portfolio already, otherwise a ValueError will raise.
 '''
        pos = self.positions.filter(instrument = inst)
        if pos.count():
            raise ValueError('Cannot add position %s to portfolio. It is already available.' % inst)
        p = Position(portfolio = self,
                     size = size,
                     value = value,
                     dt = self.dt,
                     instrument = inst)
        return p.save()
    
    def add(self, item):
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
        p = PortfolioView(name = name,
                          user = user,
                          portfolio = root)
        return p.save()
        
    def get_tree(self):
        return [p.alldata() for p in self.positions.all()]
    

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
    
    def customAttribute(self, name):
        return getattr(self.instrument,name)
        
    
    
class PortfolioView(FinPositionBase):
    name = orm.AtomField()
    user = orm.AtomField(required = False)
    portfolio = orm.ForeignKey(Portfolio, related_name = 'views')
    
    def __str__(self):
        return '%s: %s' % (self.portfolio,self.name)
    
    def customAttribute(self, name):
        return getattr(self.portfolio,name)
    
    def addfolder(self, name):
        '''Add folder for portfolio view. Self must have holder attribute available.'''
        return PortfolioViewFolder(name = name, view = self).save()
    
    def get_tree(self):
        return [p.alldata() for p in self.folders.all()]
    
    
class PortfolioViewFolder(FinPositionBase):
    '''A Folder within a portfolio view'''
    name   = orm.AtomField()
    parent = orm.ForeignKey('self',
                            required = False,
                            related_name = 'children')
    view   = orm.ForeignKey(PortfolioView,
                            required = False,
                            related_name = 'folders')
    positions = orm.SetField(Position)
    
    def get_tree(self):
        tree = [p.alldata() for p in self.children.all()]
        [tree.append(p.alldata()) for p in self.positions.all()]
        return tree
    
    
    
class UserViewDefault(orm.StdModel):
    user = orm.AtomField()
    portfolio = orm.ForeignKey(Portfolio, related_name = 'user_defaults')
    view = orm.ForeignKey(PortfolioView, related_name = 'user_defaults')

