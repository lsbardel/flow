from jflow.utils.observer import lazyobject

from jflow.rates import log


class cacheBase(lazyobject):
    
    def __init__(self):
        super(cacheBase,self).__init__()
    
    def post_attach(self, obs):
        '''
        observable method.
        Invoked when we attach a new observer.
        Here we send an update to the observer
        '''
        obs.update()
    
    def log(self, msg, obj = None, verbose = 0):
        log.msg(msg, obj = obj or self, verbose = verbose)
        
    def err(self, e, msg = None, obj = None, sendmail = True):
        log.err(e, msg = msg, obj = obj or self, sendmail = sendmail)
    


class cacheObject(cacheBase):
    '''
    Base class for all classes in the module
    '''
    def __init__(self, cache):
        super(cacheObject,self).__init__()
        self.cache         = cache
    