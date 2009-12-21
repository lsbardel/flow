from jflow.core.cashflow import CashFlow
 
from finins import *


class CashFlowRate(CashFlow):
    '''
    A cash-flow object with an embedded rate object
    '''
    def __init__(self, priority = 1, rate = None):
        CashFlow.__init__(self)
        self.__priority = priority
        self.rate       = rate
            
    def __get_priority(self):
        return self.__priority
    priority = property(fget = __get_priority)
    
    def _available(self):
        return self.rate._available()
    
    
    