

import logging


class QmLog(object):
    
    def __init__(self, log):
        self._log = log
        
    def info(self,msg,obj=None):
        self._message(msg,obj,logging.INFO)
        
    def msg(self,msg,obj=None):
        self._message(msg,obj,logging.INFO)
    
    def warn(self,msg,obj=None):
        self._message(msg,obj,logging.WARN)
        
    def error(self,msg,obj=None):
        self._message(msg,obj,logging.ERROR)
        
    def debug(self,msg,obj=None):
        self._message(msg,obj,logging.DEBUG)
        
    def _message(self,msg,obj,lev):
        if obj == None:
            self._log.log(msg=msg,level=lev)
        else:
            self._log.log(msg='%s. %s' %(obj,msg),level=lev)
            
class QmLogTwisted(QmLog):
    
    def __init__(self, log):
        super(QmLogTwisted,self).__init__(log)
        
    def _message(self,msg,obj,lev):
        if obj == None:
            self._log.msg(msg,logLevel=lev)
        else:
            self._log.msg('%s. %s' %(obj,msg),logLevel=lev) 
    

__qmlog = None

def get(withTwisted = False):
    global __qmlog
    if __qmlog != None:
        return __qmlog
    else:
        if withTwisted:
            return _get_twisted_log()
        else:
            plog = logging.getLogger()
            __qmlog = QmLog(plog)
            return __qmlog
    
def __get_twisted_log():
    global __qmlog
    from twisted.python import log
    observer = log.PythonLoggingObserver()
    observer.start()
    __qmlog = QmLogTwisted(log)
    return __qmlog
    