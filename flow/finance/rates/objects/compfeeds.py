
from composite import compositeRate

__all__ = ['ccypair']

class compfeedRate(compositeRate):
    '''
    This is a scalar rate which
    depends on other rates 
    '''
    def __init__(self, *args, **kwargs):
        super(compfeedRate,self).__init__(*args, **kwargs)
        self.value = None
        
    def baserate(self):
        return self.inputrates.get(self.holder.baseFactory.code())
    
    def get(self, *args, **kwargs):
        self.pingrate()
        return self.value


class ccypair(compfeedRate):
    
    def __init__(self, *args, **kwargs):
        super(ccypair,self).__init__(*args, **kwargs)
    
    def refresh_rate(self):
        '''
        Got an update
        '''
        try:
            fxcross = self.rates.values()[0]
            self.value = fxcross.spot(self.factory.c1,self.factory.c2)
        except:
            pass
    
    