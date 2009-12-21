
from twisted.internet import defer


class DeferredInChain(defer.Deferred):
    '''
    An class which facilitate a deferred chain
    '''
    def __init__(self, parent = None):
        defer.Deferred.__init__(self)
        self.parent    = parent
        self.children  = {}
        self.results   = {}
        self.errors    = []
        
    def code(self):
        raise NotImplementedError
        
    def get_chainresult(self, res):
        if self.parent:
            self.parent.addresult(self, res)
            
    def get_chainerror(self, res):
        if self.parent:
            self.parent.adderror(self, res)
    
    def chaincallback(self):
        if self.parent:
            self.addCallback(self.get_chainresult).addErrback(self.get_chainerror)
            
    def addDeferred(self, d):
        if isinstance(d,DeferredInChain):
            self.children[d.code()] = d
        
    def setcallbacks(self):
        '''
        Set the callbacks on children.
        Loop over children and add the cahin callbacks
        '''
        for d in self.children.values():
            d.chaincallback()
            
    def setresult(self, d, res):
        self.results[d.code()] = res
    
    def adderror(self, d, er):
        self.children.pop(d.code())
        self.errors.append(er)
        if not self.children:
            self.finished()
            
    def addresult(self, d, res):
        self.children.pop(d.code())
        self.setresult(d,res)
        if not self.children:
            self.finished()
            
    def finished(self):
        if self.errors:
            err = self.failed()
            self.errback(err)
        else:
            result = self.success()
            self.callback(result)
    
    def success(self):
        '''
        Return the results list.
        '''
        return self.results
    
    def failed(self):
        '''
        Needs to be implemented by derived classes
        '''
        pass
        
        
    