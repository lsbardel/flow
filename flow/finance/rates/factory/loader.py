'''Classes for asyncronous loading of rates form
data vendors interfaces
'''
from jflow.utils.observer import mulobserver
from jflow.utils.decorators import runInThread, threadSafe
from jflow.utils.tx import DeferredInChain
from jflow.core.field import fieldproxy

from twisted.internet import defer


def histloader(factory, start, end, period, vfid, parent = None):
    '''
    Rate History loader function.
    Helper function to load rates into cache
    '''
    if factory.hrates:
        return mhistloader(factory, start, end, period, vfid, parent)
    else:
        return shistloader(factory, start, end, period, vfid, parent)
    

class bhistloader(DeferredInChain):
    '''
    Base class for loading data
    '''
    def __init__(self, factory, start, end, period, vfid, parent = None):
        '''
        deferred must have a callBack method (twisted deferred)
        '''
        DeferredInChain.__init__(self, parent = parent)
        self.factory           = factory
        self.cache             = factory.cache
        self.realstart         = start
        self.realend           = end
        self.start             = start
        self.end               = end
        self.period            = period
        self.vfid              = vfid
        self._load             = False
        self._loading_dates()
            
    def _loading_dates(self):
        if self.vfid:
            self._load, self.start, self.end, self.realstart, self.realend = self.factory._loading_dates(self.start, self.end, self.vfid)
    
    def __str__(self):
        return self.code()
    
    def __repr__(self):
        return self.code()
    
    def code(self):
        return str(self.vfid)
    
    def load(self):
        '''
        Load data.
        If there is no need to load rates we invoke the finished method
        '''
        if self._load:
            self._do_load()
        else:
            self.finished()
            #self.handleupdate()
        return self
    
    def _do_load(self):
        raise NotImplementedError

    def __get_holder(self):
        return self.factory.holder
    holder = property(fget = __get_holder)
    
    def success(self):
        '''
        The loading has been succesfull.
        The dictionary self.results contains timeseries of underlying rates.
        We pass this to the Factory to deal with
        '''
        return self.handleupdate(self.results)
    
    def create_result(self, res = None):
        '''
        The loader has finished and this function has been called.
        The loader is ready to create the result.
        Call the factory-specific handler
        '''
        holder      = self.holder
        if self.realstart == self.realend:
            result = holder.get(self.realstart)
        else:
            result = holder.getts(self.realstart,
                                  self.realend,
                                  self.vfid)
        self.result = result
    
    def handleupdate(self, res = None):
        '''
        The loader has finished and this function has been called.
        The loader is ready to create the result.
        Call the factory-specific handler
        '''
        res = self.factory._handleresult(self, res)
        holder      = self.holder
        if self.realstart == self.realend:
            result = res.get(self.realstart)
        else:
            result = holder.getts(self.realstart,
                                  self.realend,
                                  self.vfid)
        return result



class shistloader(bhistloader):
    '''
    loader for a single data
    '''
    def __init__(self, *args):
        bhistloader.__init__(self, *args)
    
    def __handleupdate(self, res):
        if isinstance(res,defer.Deferred):
            res.addCallbacks(self.__handleupdate,self.errback)
        else:
            self.results = res
            self.finished()
        
    def _do_load(self):
        '''Send the request to the data loader Thread Pool'''
        self.factory.loaderpool.deferToThread(self.__handleupdate,
                                              self.errback,
                                              self.factory._performload,
                                              self)
    
    
    
class mhistloader(bhistloader):
    '''
    Loader for fields with multiple underlyings
    '''
    def __init__(self, *args):
        bhistloader.__init__(self, *args)
        
    def _do_load(self):
        '''
        Perform the rate loading
        '''
        hrates = self.factory.hrates
        for rf in hrates:
            lf = rf.get_history(self.realstart,
                                self.realend,
                                self.vfid.field,
                                self.vfid.vendor,
                                parent = self)
            self.addDeferred(lf)
        self.setcallbacks()
    
    def setresult(self, cl, res):
        '''override the setresult method'''
        rh = cl.holder
        self.results[cl.code()] = (rh,res)
    
    
        