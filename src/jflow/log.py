import logging
from jflow.conf import settings
from jflow.utils.decorators import lazyattr

def get_logger(name):
    return logging.getLogger(name = str(name))


def setup_logging(name):
    '''
    Setup logging for jflow
    name is the application name is using jflow
    '''
    logger = logging.getLogger()
    if logger.handlers:
        return get_logger(name)
    ch     = logging.StreamHandler()
    format = getattr(settings,'LOGGING_FORMAT')
    ch.setFormatter(logging.Formatter(format))
    logger.setLevel(settings.LOGGING_LEVEL)
    logger.addHandler(ch)
    return get_logger(name)
    
    
class LoggingClass(object):
    
    def __get_logger(self):
        return get_logger(self)
    logger = property(__get_logger)
    
    def __repr__(self):
        return '%s | %s' % (self.__class__.__name__,self.description())
    
    def description(self):
        return ''
    
    def __str__(self):
        return self.__repr__()
    
    def err(self, msg, obj = None):
        obj  = obj or self
        msgt = '%s - %s' % (obj,msg)
        if isinstance(msg,Exception):
            msg = msg.__class__(msgt)
        else:
            msg = msgt
        self.logger.err(msg)