from twisted.internet import task

from jflow.utils import servers


class ConnectionPool(servers.ConnectionPool):
    '''
    Connection Pool Manager.
    It maintains a pool of remote server connections
    '''
    def __init__(self, *args, **kwargs):
        super(ConnectionPool,self).__init__(*args, **kwargs)
    
    def setupconnloop(self):
        tk = task.LoopingCall(self.connect)
        tk.start(self.conn_loop_freq)
        self.conntask = tk