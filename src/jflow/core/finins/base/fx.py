

from finins import *

__all__ = ['fxins']


class fxins(finins):
    
    def __init__(self, pair = None, *args, **kwargs):
        super(fxins,self).__init__(*args, **kwargs)
        self.pair = pair
        

        

        