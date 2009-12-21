from django.utils.datastructures import SortedDict
from base import PositionBase

__all__ = ['Portfolio']


class Portfolio(PositionBase):
    
    def __init__(self, *args, **kwargs):
        super(Portfolio,self).__init__(*args, **kwargs)
        self._positions = SortedDict()
        
    def has_key(self, key):
        return self._positions.has_key(str(key))
    
    def _trim(self,c):
        return str(c).upper()
    
    def get(self, key, retdef = None):
        return self._positions.get(self._trim(key), retdef)
    
    def add(self, item):
        if isinstance(item,PositionBase):
            c = self._trim(item.code)
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
    
        