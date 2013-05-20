from django.conf import settings
from jflow.db.utils import function_module
from jflow.rates import log

class PositionException(Exception):
    
    def __init__(self, obj, e, msg):
        self.obj  = obj
        self.type = e.__class__.__name__
        self.err  = str(e)
        self.msg  = msg
        
    def __repr__(self):
        return 'Error in %s while %s. %s: %s' % (self.obj.__class__.__name__, self.msg, self.type, self.err)
    
    def __str__(self):
        return self.__repr__()
    
class PositionObjectException(Exception):
    
    def __init__(self, obj, e, msg = None):
        self.obj  = obj
        self.type = e.__class__.__name__
        self.err  = str(e)
        self.msg  = msg
        
    def __repr__(self):
        name = '%s - %s' % (self.obj.__class__.__name__,self.obj)
        if self.msg:
            return 'Error in %s. %s. %s: %s' % (name, self.msg, self.type, self.err)
        else:
            return 'Error in %s. %s: %s' % (name, self.type, self.err)
    
    def __str__(self):
        return self.__repr__()