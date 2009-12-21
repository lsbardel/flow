
import urlparse


class connsetting(object):
    '''
    Helper class for creating remote connections
    '''
    def __init__(self, address = 'localhost:8000', method = 'tcp'):
        self.method = method
        addr = address.split(':')
        self.hostname = addr[0]
        if len(addr) == 2:
            self.port = int(addr[1])
        else:
            self.port = 8000
        
    def connect(self):
        if self.method == 'tcp':
            return self.tcp_connect()
        else:
            raise NotImplementedError

    def tcp_connect(self):
        raise NotImplementedError
    

class txconnsettings(connsetting):
    
    def __init__(self, factory_class = None, **kwargs):
        self.factory_class = factory_class
        super(txconnsettings,self).__init__(**kwargs)
        
    def tcp_connect(self):
        '''
        Connect factory to remote server
        '''
        from twisted.internet import reactor
        fc = self.factory_class()
        reactor.connectTCP(self.hostname,self.port,fc)
        return fc
        
        
class txpbconnection(connsetting):
    '''
    Shortcut class for connecting a twisted pb client to a remote pb server
    '''
    def __init__(self, factory_class = None, **kwargs):
        if not factory_class:
            from twisted.spread import pb
            self.factory_class = pb.PBClientFactory
        super(txconnsettings,self).__init__(**kwargs)
    
    def tcp_connect(self):
        '''
        Connect factory to remote server
        '''
        from twisted.internet import reactor
        fc = self.factory_class()
        reactor.connectTCP(self.hostname,self.port,fc)
        fc.getRootObject()
        return fc
    