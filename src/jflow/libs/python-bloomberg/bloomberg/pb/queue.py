from threading import Lock

from jflow.utils.tx import runInThread
from jflow.utils.decorators import threadSafe


class SingleThreadQueueUpdate(object):
    
    def __init__(self, flushlen = 30, flush = 10):
        self.lock     = Lock()
        self.__queue  = []
        self.running  = False
        self.flushlen = flushlen
        self.flush    = flush
    
    @threadSafe
    def add(self, update, args = None):
        self.__queue.append((update,args))
        if not self.running:
            self.run()
    
    def __str__(self):
        return '%s - %s' % (self.__class__.__name__, self.idx)
    
    @runInThread
    def run(self):
        self.running = True
        while self.running:
            if len(self) > self.flushlen:
                self.__queue = self.__queue[self.flush:]
            try:
                update, args = self.__queue.pop(0)
            except:
                self.running = False
                
            try:
                update(args)
            except:
                pass
    
    def __len__(self):
        return len(self.__queue)

