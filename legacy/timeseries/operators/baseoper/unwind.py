
class BadConcatenation(Exception):
    '''Error cause by bad concatentaiuon types'''
    def __init__(self, type1, type2):
        msg = 'Failed to concatenate %s with %s' % (type1,type2)
        super(BadConcatenation,self).__init__(msg)
        
class FunctionArgumentError(Exception):
    
    def __init__(self, function, msg):
        msg = 'Argument error in function "%s": %s' % (function,msg)
        super(FunctionArgumentError,self).__init__(msg)


class unwindData(object):
    
    def __init__(self, data = None, label = None, type = "unknown"):
        self.data    = data
        self.label   = label or str(data)
        self.type    = type
        
    def iterable(self):
        try:
            len(self)
            return True
        except:
            return False
        
    def __str__(self):
        return self.label
        
    def internal_data(self):
        '''
        Return raw internal data
        '''
        return self.data
    
    def apply(self):
        return self.internal_data()
    
    def json(self):
        '''
        return object as JSON
        '''
        data = self.apply()
        return {'type':  self.type,
                'data':  data,
                'label': self.label}
    
    
class numberData(unwindData):
    '''
    simple Number
    '''
    def __init__(self, val):
        super(numberData,self).__init__(val, type = "number")

class stringData(unwindData):
    '''
    simple String
    '''
    def __init__(self, val):
        super(stringData,self).__init__(val, type = "string")
        
class boolData(unwindData):
    '''
    simple boolean
    '''
    def __init__(self, val):
        super(boolData,self).__init__(val, type = "boolean")    
    
class keyValue(unwindData):
    '''
    a Key-Value relationship
    '''
    def __init__(self, key, val):
        super(keyValue,self).__init__(val, key, type = "keyvalue")
        
    def __str__(self):
        return '%s = %s' % (self.label, self.data)
    
    def internal_data(self):
        return {self.label: self.data}
        
    
    
class tsData(unwindData):
    '''
    a univariate time-series data
    '''
    def __init__(self, data = None, label = None):
        super(tsData,self).__init__(data, label, type = "timeseries")
    
    def applyoper(self):
        #from jflow.core.timeseries import tsoper
        #if isinstance(self.data,tsoper):
        self.data = self.data.apply()
            
    def apply(self):
        from jflow.core.timeseries import toflot
        self.applyoper()
        return [{'label': self.label,
                 'data': toflot(self.data)}]
 
    

class listBase(unwindData):
    
    def __init__(self, **kwargs):
        super(listBase,self).__init__(data = [], **kwargs)
        
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return self.data.__iter__()
    
    def append(self, data):
        raise NotImplementedError
    
    
class listData(listBase):
    
    def __init__(self, label = None):
        super(listData,self).__init__(label = label, type = "list")
        
    def append(self, data):
        self.data.append(data)
        
    def json(self):
        '''
        return object as JSON
        '''
        res = []
        for d in self.data:
            res.append(d.json())
        return res
    
        
class sameListData(listBase):
    
    def __init__(self, label = None):
        super(sameListData,self).__init__(label = label)
        
    def append(self, data):
        if not self.data:
            self.data.append(data)
            self.type = data.type
        else:
            if data.type != self.type:
                raise BadConcatenation(self.type,data.type)
            self.data.append(data)
    
    def apply(self):
        res = []
        for d in self.data:
            res.extend(d.apply())
        return res
    
    
        
class covarTsData(unwindData):
    
    def __init__(self, data = None, label = None):
        super(tsData,self).__init__(data, label, type = "covariance-timeseries")
        self.covar = sameListData(str(self))
        self.var = sameListData(str(self))
        
    def apply(self):
        from jflow.core.timeseries import toflot
        return [{'label': self.label,
                 'data': toflot(self.data)}]


class covarMatrix(unwindData):
    
    def __init__(self, data = None, label = None):
        super(tsData,self).__init__(data, label, type = "covariance-timeseries")
        
    def apply(self):
        from jflow.core.timeseries import toflot
        return [{'label': self.label,
                 'data': self.tojson(self.data)}]
        
    def tojson(self):
        pass
    