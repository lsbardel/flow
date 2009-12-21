
from base import PositionBase

__all__ = ['cash_account']

class cash_account(PositionBase):
    
    def __init__(self, dbobj = None):
        PositionBase.__init__(self, dbobj = dbobj)
        self.__cash = {}
        
    def __iter__(self):
        return self.__cash.__iter__()
    
    def iteritems(self):
        return self.__cash.iteritems()
        
    def add(self, cur, ammount):
        cash    = self.__cash
        ca = cash.get(cur,0.0) + ammount
        cash[cur] = ca
        
    def update(self, ca):
        if isinstance(ca,cash_account):
            for cur,amm in ca.iteritems():
                self.add(cur,amm)
        