

from threading import RLock


def get_lock(lock = None):
    if lock == None:
        return RLock()
    else:
        return lock

class lockbase(object):
    
    def __init__(self, lock = None):
        self.__lock = get_lock(lock)
            
    def __get_lock(self):
        return self.__lock
    lock = property(fget = __get_lock)
    
    
class loglock(lockbase):
    
    def __init__(self, lock = None, log = None):
        super(loglock,self).__init__(lock = lock)
        self.__log  = log
        if self.__log == None:
            from qmpy.core import qmlog
            self.__log = qmlog.get()
    
    def log(self, msg):
        self.__log.info(msg)