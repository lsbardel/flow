from jflow.utils.observer import lazyobject
from jflow.db.trade.models import Position

from jflow.utils.tx import runInThread

from logger import log, PositionObjectException

import basecache 


def listpop(li, elem):
    idx = 0
    for el in li:
        if el == elem:
            return li.pop(idx)
        idx += 1
    return None


def extract(obj, code, jsv):
    attr = getattr(obj,code,None)
    if attr:
        if callable(attr):
            try:
                attr = attr()
            except:
                attr = '#Error'
        jsv.append(attr)
        return True
    return False


class jsonTrade(basecache.cacheObject):
    '''
    Base class for JSON portfolio objects.
    This class exposes two methods which may be reimplemented by
    subclasses:
        _build          for building the object after it has been created
        addcallback     for adding callback when the building process is finished
    '''
    def __init__(self, cache):
        super(jsonTrade,self).__init__(cache)
        self.__building    = False
        self.json          = {}
        self._callbacks    = []
        
    def __unicode__(self):
        return u'%s' % self.cache
    
    def __str__(self):
        return str(self.__unicode__())
    
    def __repr__(self):
        return str(self)
    
    def build(self, inthread = False):
        '''
        Build the object. This method will eventually call self._build
        '''
        if self.__building:
            return
        self.__building = True
        if self.inthreadoverride(inthread):
            self._build_in_thread()
        else:
            self._build_json()
    
    @runInThread
    def _build_in_thread(self):
        self._build_json()
        
    def _build_json(self):
        try:
            self._build()
        except Exception, e:
            self.err(e)
    
    def __get_building(self):
        return self.__building
    building = property(fget = __get_building)
    
    def addcallback(self, cbfun):
        if self.__building:
            self._callbacks.append(cbfun)
        else:
            try:
                cbfun(self)
            except Exception, e:
                self.err(e)
                
    def rjson(self):
        '''
        Return the json object.
        before that. It updates the object if required
        '''
        self.refresh()
        return self.json
    
    def jsonDescription(self, msg):
        return {'error': False,
                'object': str(self),
                'msg': str(msg)}
        
    def _build(self):
        '''
        needs implementing by derived classes
        '''
        pass
    
    def inthreadoverride(self, inthread):
        return inthread
    
    def _closebuild(self):
        self.__building = False
        cbs = self._callbacks
        while cbs:
            cbfun = cbs.pop()
            try:
                cbfun(self)
            except Exception, e:
                self.err(e)
    
    
    
class positionBase(jsonTrade):
    
    def __init__(self, cache, obj, dte):
        super(positionBase,self).__init__(cache)
        self.dbobj    = obj
        self.dte      = dte
        self.id       = self.cache.get_object_id(self.dbobj)
        self.code     = self.dbobj.code
        self.rowdata  = []
        
    def __unicode__(self):
        return u'%s' % self.code
        
    def __setitem__(self, code, value):
        d = self.cache.displaydict.get(code,None)
        N = len(self.rowdata)
        if d is not None and N > d:
            self.rowdata[d] = value
            
    def __getitem__(self, code):
        d = self.cache.displaydict.get(code,None)
        N = len(self.rowdata)
        if d is not None and N > d:
            return self.rowdata[d]
        else:
            return ''

    def reregister(self):
        self.rowdata = []
        self.register()
        
    def register(self):
        '''
        Attach aggposition instance to fininst in order to receive updates
        '''
        jsv = self.rowdata
        if jsv:
            return False
        objs = self.cache.display
        for el in objs:
            code = el.code
            # Try self first
            attr = extract(self,code,jsv)
            if not attr:
                if not self.register2(code,jsv):
                    jsv.append('#N/A')
        self.setstaticjson()
        return True
        
    def setstaticjson(self):
        json          = self.json
        json['id']    = self.id
        json['code']  = self.code
        json['row']   = self.rowdata
        
    def register2(self, code, jsv):
        jsv.append("")
        return True
    
    def refresh_me(self):
        '''
        observer method. called when a refresh is needed
        '''
        self.register()