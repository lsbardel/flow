
from icash import *
from jflow.core.timeseries import dateseries as InnerCF 


class CashIterator(object):
    
    def __init__(self, inner):
        self.__iter = inner.__iter__()
        
    def __iter__(self):
        return self

    def _nextok(self):
        v = self.__iter.next()
        return v.value
    
    def next(self):
        try:
            return self._nextok()
        except StopIteration:
            raise StopIteration      


class CashFlowBase(object):
    '''
    Cash flow base class
    '''
    def __init__(self, duplicate = True):
        if duplicate:
            self.__inner = InnerCF2()
        else:
            self.__inner = InnerCF()
        
    def __get_inner(self):
        return self.__inner
    inner = property(fget = __get_inner)
        
    def __str__(self):
        return '%s' % self.__inner
    
    def __repr__(self):
        return '%s %s' % (self.__class__.__name__,self)
    
    def __iter__(self):
        return self.__inner.__iter__()
    
    def itervalues(self):
        return CashIterator(self.__inner)
    
    def __getitem__(self, idx):
        return self.__inner[idx].value
        
    def add(self, cf):
        pass
            
    def __get_enddate(self):
        c = self.__inner
        N = len(c)
        if N:
            return c[N-1].key
        else:
            return None
    enddate = property(fget = __get_enddate)
        
    def __get_startdate(self):
        c = self.__inner
        if len(c):
            return c[0].key
        else:
            return None
    startdate = property(fget = __get_startdate)
    
    def __len__(self):
        return len(self.__inner)
    
    def has_date(self, dte):
        return self.__inner.has_key(dte)



class CashFlow(CashFlowBase):
    
    def __init__(self):
        CashFlowBase.__init__(self,True)
    
    def add(self, cf):
        if isinstance(cf,icash):
            self.inner.add(cf.date(), cf)
            
    def __get_priority(self):
        return self.__priority
    priority = property(fget = __get_priority)
    
        