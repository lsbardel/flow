from twisted.internet import defer
from twisted.spread.pb import *

from jflow.utils.observer import observer


class tempref(Referenceable):
    '''
    A temporary referenceable object with a callback mechanism.
    This object can be used when a remote call run on a thread and
    therefore does not return anything.
    '''
    _requests = []
    
    def __init__(self):
        self.deferred = defer.Deferred()
        tempref._requests.append(self)
    
    def remote_update(self, args):
        '''
        Remote update.
        The feed gets an update from the remote object
        '''
        if args:
            res = self.handleupdate(args)
            if self in tempref._requests:
                tempref._requests.remove(self)
            self.deferred.callback(res)
    
    def handleupdate(self, args):
        return None


class PbReconnectingClientFactory(PBClientFactory):
    '''
    A Perspective Broker reconnecting client factory
    '''    
    def __init__(self, noisy = False, *args, **kwargs):
        PBClientFactory.__init__(self, *args, **kwargs)
        self.noisy        = noisy
        self.connector    = None
        
    def startedConnecting(self, connector):
        '''
        Called the first time we try to connect
        '''
        self.connector = connector
    
    def __str__(self):
        if self.connector:
            return '%s:%s' % (self.connector.host,self.connector.port)
        else:
            return 'PB client Factory'
    
    def isconnected(self):
        if self._broker:
            return True
        else:
            return False
        
    def clientConnectionFailed(self, *args, **kwargs):
        PBClientFactory.clientConnectionFailed(self, *args, **kwargs)
        
    def clientConnectionLost(self, *args, **kwargs):
        PBClientFactory.clientConnectionLost(self, *args, **kwargs)
        self.clenup()
        
    def clenup(self):
        pass
        


class remote_observer_wrap(observer):
    '''
    This object wrap a remote pb.Referenceable object
    in order to create a local lazyobject.
    The remote object needs to have implemented the
      remote_update method
    '''
    def __init__(self, remote, **kwargs):
        super(remote_observer_wrap,self).__init__(**kwargs)
        self.remote = remote
    
    def _append_subject(self, subject):
        self.subject = subject
        
    def doupdate(self, args = None):
        '''
        Method called by the remote object to update self
        '''
        if self.remote:
            try:
                self.remote.callRemote('update',args)
            except Exception:
            #except DeadReferenceError:
                self.subject.detach(self)


class pbremote(Root):
    '''
    Base class for a remote Perspective Broker
    with an uptime function 
    '''
    def __init__(self, server):
        self.server  = server
        
    def __repr__(self):
        return self.server.__repr__()
    
    def remote_uptime(self, args = None):
        try:
            return self.server.uptime()
        except:
            return 0
    
    def listen(self, port, poolsize = 0):
        from twisted.internet import reactor
        self.factory = PBServerFactory(self)
        reactor.listenTCP(port, self.factory)
        if poolsize > 0:
            reactor.suggestThreadPoolSize(poolsize)
        return reactor
    
    def kill(self):
        from twisted.internet import reactor
        self.server.kill()
        reactor.stop()