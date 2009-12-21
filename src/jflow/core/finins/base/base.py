from jflow.utils.observer import lazyobject
from jflow.utils.decorators import lazyattr
from jflow.utils.baseval import baseval

__all__ = ['PositionBase']


class PositionBase(lazyobject):
    '''
    Base Position object
    '''
    def __init__(self,
                 dbobj = None,
                 code  = None,
                 label = None,
                 id    = None,
                 open_date = None,
                 display   = None,
                 *args, **kwargs):
        super(PositionBase,self).__init__(*args, **kwargs)
        self.dbobj     = dbobj
        self.id        = id
        self.open_date = open_date
        self.display   = display
        if dbobj != None:
            self.__code  = code or self.dbobj.code
            self.__label = label or self.__code
        else:
            self.__code   = code
            self.__label  = label or code
        
    def __get_code(self):
        return self.__code
    code = property(fget = __get_code)
    
    def __get_label(self):
        return self.__label
    label = property(fget = __get_label)
    
    def __unicode__(self):
        return u'%s' % self.code
    
    def __str__(self):
        return str(self.__unicode__())
    
    def __repr__(self):
        return '%s. %s' % (self.__class__.__name__, self)
    
    def end_date(self):
        return ''
    
    def tags(self):
        return ''
    
    def name(self):
        return self.dbobj.name()
    
    def description(self):
        return self.dbobj.get_description()
    
    def ccy(self):
        try:
            return self.dbobj.ccy()
        except:
            return None
    
    def display_position(self):
        if self.display:
            ret = {}
            for de in self.display:
                try:
                    val = getattr(self, de.code)
                    if callable(val):
                        val = val()
                    val = baseval(val)
                except:
                    val = None
                ret[de.code] = {'label':de.name,
                                'value':val}
            return ret
        else:
            return None
    
    def get_portfolio(self):
        return None
    
    def dict(self):
        return {'display':    self.display_position(),
                'portfolio':  self.get_portfolio(),
                'name':       self.code,
                'label':      self.label,
                'id':         self.id}
        