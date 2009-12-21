
__all__ = ['get','tsoperator']


def get(oper, retval = None):
    global _operations
    oper = str(oper).lower()
    op   = _operators.get(oper,retval)
    if op != retval:
        return op()
    else:
        return None
    
    

class TSoperatorMeta(type):
    '''
    PyQuery plugins type class
    '''
    def __new__(cls, name, bases, attrs):
        super_new = super(TSoperatorMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, TSoperatorMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)
        
        attr_meta = attrs.pop('Meta', None)
        abstract  = getattr(attr_meta, 'abstract', False)
        
        new_class = super_new(cls, name, bases, attrs)
        name      = new_class.__name__.lower()
        if not abstract:
            op   = _operators.get(name)
            if op:
                raise KeyError("Timeserie operator %s already registered" % op)
            _operators[name] = new_class
            
        return new_class
        
        
        
class tsoperator(object):
    '''
    Base class for time-series operators
    '''
    __metaclass__ = TSoperatorMeta
    
    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return self.__class__.__name__
    
    def __unicode__(self):
        return u'%s' % self
    
    def description(self):
        return ''
    
    def unwind(self, *args, **kwargs):
        self.unwind = kwargs.pop('unwind_objects',None)
        return self.apply(*args, **kwargs)
    
    def apply(self, *args, **kwargs):
        raise NotImplementedError
    
    def newts(self):
        from jflow.core.timeseries import numericts
        return numericts()
    

_operators = {}