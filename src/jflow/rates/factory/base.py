from jflow.core.rates import rateFactory, idFactory, ccypairFactory, cacheObject


class scalarFactoryFactory(cacheObject):
    '''
    A factory class for creating specific scalar rates factories
    '''     
    def get(self, id = None, proxy = None, ccy = None):
        if id:
            return idFactory(id, ccy)
        else:
            raise NotImplementedError
    
