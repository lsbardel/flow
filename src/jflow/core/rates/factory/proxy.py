from factory import compositeFactory
from jflow.core.rates import objects

__all__ = ['proxyRateFactory']


class proxyRateFactory(compositeFactory):
    '''
    Base class for Factories of proxy rates.
    Proxy rates are scalar rates which depends on other rates
    '''
    def __init__(self, cache, *codes):
        super(proxyRateFactory,self).__init__(cache,*codes)
    
    def isproxy(self):
        return True
    
    def _post_make(self, cr):
        '''
        Called by self when building historical rates
        '''
        cr.baserate = self.baseHistory.get(cr.dateobj())
        if cr.baserate == None:
            return None
        else:
            return cr   
    