
from jflow.core import dates



class icash(object):
    '''
    cash interface
    '''
    def notional(self):
        '''
        The notional ammount
        '''
        return 0.
    
    def __repr__(self):
        c = self.currency()
        if c:
            return '%s %s %s' % (self._descr(), c, self.cash())
        else:
            return '%s %s' % (self._descr(), self.cash())
    
    def __str__(self):
        return self.__repr__()
    
    def _descr(self):
        return '%s' % self.__class__.__name__
    
    def ccy(self):
        return None
    
    def date(self):
        raise NotimplementedError
    
    def isdummy(self):
        return False
    
    def cash(self):
        '''
        The cash ammount
        '''
        return self.notional()
    
    def dcf(self):
        '''
        Day count fraction. Used for certain type of cash
        '''
        return 0.
    
    def ndcf(self):
        '''
        Notional times the day count fraction
        '''
        return self.notional()*self.dcf()


