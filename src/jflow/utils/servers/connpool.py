from iserver import Iserver

def randominteger(N):
    from random import random
    r = N*random()
    return int(r)



class ConnectionPool(Iserver):
    '''
    Connection Pool Manager.
    It maintains a pool of remote server connections
    '''
    def __init__(self, conn_loop_freq = 5):
        '''
        conn_loop_freq frequency in seconds for checking servers connection
        '''
        self.servers = {}
        self.conn_loop_freq = 5
        if self.conn_loop_freq > 0:
            self.setupconnloop()
    
    def setupconnloop(self):
        pass
    
    def get_servers(self):
        raise NotImplementedError
    
    def get(self):
        '''
        Get a random server from the pool
        '''
        co = self.connected().values()
        N  = len(co)
        if N == 0:
            return None
        elif N == 1:
            return co[0]
        else:
            n = randominteger(N)
            return co[n]
        
    def connect(self):
        '''
        get new list of servers (It may have changed).
        Loop ovber new list.
        If server is not available is added to the list.
        Check if server is connected
        '''
        servs = self.get_servers()
        for k,v in servs.items():
            s = self.servers.get(k,None)
            if s == None or not s.isconnected():
                s = v.connect()
                self.servers[k] = s
                
    def isconnected(self):
        return len(self.connected()) > 0
    
    def connected(self):
        co = {}
        for k,s in self.servers.items():
            if s.isconnected():
                co[k] = s
        return co
    
    def disconnect(self):
        for c in self.servers.values():
            c.disconnect()
            
    