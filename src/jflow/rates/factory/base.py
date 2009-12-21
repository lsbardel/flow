from jflow.core.rates import rateFactory, idFactory, ccypairFactory, cacheObject


class scalarFactoryFactory(cacheObject):
    '''
    A factory class for creating specific scalar rates factories
    '''
    def __init__(self, cache):
        super(scalarFactoryFactory,self).__init__(cache)
        
    def get(self, id = None, proxy = None, ccy = None):
        if id:
            return idFactory(self.cache, id, ccy)
        else:
            raise NotImplementedError
    
