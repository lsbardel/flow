
import cPickle
from nuts import json_value

class baseArgs(object):
    '''
    Class for handling return Arguments across the wire
    '''
    arguments_str = 'arguments'
    
    def __init__(self, arguments = None):
        if arguments == None:
            self.__arguments = {}
        else:
            try:
                self.__arguments = arguments.get(self.arguments_str, {})
            except:
                self.__arguments = {}
    
    def __get_arguments(self):
        return self.__arguments
    arguments = property(fget = __get_arguments)
    
    def __str__(self):
        return str(self.__arguments)
    
    def __repr__(self):
        return self.__str__()
    
    def __setitem__(self, key, val):
        try:
            self.__arguments[str(key)] = val
        except:
            pass
        
    def __getitem__(self, key):
        return self.get(key,None)
    
    def get(self, key, ret=None):
        return self.__arguments.get(str(key), ret)
    
    def get_dict(self):
        pd = self.__pickable_dict()
        st = {self.arguments_str:  pd}
        return st
    
    def set_dict(self, st):
        self.__arguments = st[self.arguments_str]
        
    def _dumps(self):
        return self.get_dict()
    
    def dump(self):
        return cPickle.dumps(self,2)
        
    def __getstate__(self):
        return self._dumps()
    
    def __setstate__(self, obj):
        self.set_dict(obj)
        
    def __pickable_dict(self):
        ars = self.__arguments
        pdi = {}
        for k,v in ars.iteritems():
            pdi[k] = json_value(v)
        return pdi
        
    def __get_error(self):
        return self.get('error', False)
    error = property(fget = __get_error)
    
    def __get_result(self):
        return self.get('result', False)
    result = property(fget = __get_result)
    
    def __get_result_error(self):
        r = self.error
        if r:
            return r
        else:
            return self.result
    value = property(fget = __get_result_error)
    

class errorArg(baseArgs):
    
    def __init__(self, error=True, result = None):
        super(errorArg,self).__init__()
        self['error'] = str(error)
        if result != None:
            self['result'] = result


class Result(baseArgs):
    
    def __init__(self, result = ''):
        super(Result,self).__init__()
        self['result']    = result
    
class Args(baseArgs):
    
    def __init__(self, **kwargs):
        super(Args,self).__init__()
        for k,v in kwargs.iteritems():
            self[k] = v