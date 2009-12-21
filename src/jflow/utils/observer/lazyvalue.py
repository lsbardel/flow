
from observer import lazyobject

__all__ = ['lazycache','lazyvalue']


class lazycache(lazyobject):
    '''
    A special lazyobject object.
    This object wrap a cache dictionary-type object so that
    when it receives updates it write them into the cache key.
    '''
    def __init__(self, cache = None, key = None, *args, **kwargs):
        super(lazycache,self).__init__(*args, **kwargs)
        self.cache = cache
        self.key   = key
    
    def update_me(self, args=None):
        '''
        Set the value of the cache key
        '''
        from retargs import baseArgs, Result
        if not isinstance(args, baseArgs):
            args = Result(result = args)
        self.cache.set(self.key, args.get_dict())
        return args

class lazyvalue(lazyobject):
    
    def __init__(self, value = 0., code = '', description = '', *args, **kwargs):
        super(lazyvalue,self).__init__(*args, **kwargs)
        self.__value     = value
        self.__code      = code
        self.description = description
        
    def update_me(self, args):
        self.__value = args
    
    def __get_value(self):
        return self.__value
    value = property(fget = __get_value)
    
    def as_bp(self):
        return 10000*self.value
    
    def as_pc(self):
        return 100*self.value
    