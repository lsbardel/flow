import logging
from jflow.conf import settings
from jflow.utils.decorators import lazyattr

if logging.thread:
    default_format = "%(asctime)s - (p=%(process)s,t=%(thread)s) - %(levelname)s - %(name)s - %(message)s"
else:
    default_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

def get_logger(name = None):
    prefix = settings.LOGGING_PREFIX
    if name:
        if prefix:
            prefix = '%s ' % prefix
        name = '%s%s' % (prefix,name)
    else:
        name = prefix
    return logging.getLogger(name = name)


def setup_logging(name = None):
    '''
    Setup logging for jflow
    name is the application name is using jflow
    '''
    logger = get_logger(name)
    if logger.handlers:
        return
    ch     = logging.StreamHandler()
    logger = logging.getLogger(name = name)
    format = getattr(settings,'LOGGING_FORMAT',default_format)
    ch.setFormatter(logging.Formatter(format))
    logger.setLevel(settings.LOGGING_LEVEL)
    logger.addHandler(ch)
    
    
class LoggingClass(object):
    
    def __get_logger(self):
        return get_logger(self)
    logger = property(__get_logger)
    
    def err(self, msg, obj = None):
        obj  = obj or self
        msgt = '%s - %s' % (obj,msg)
        if isinstance(msg,Exception):
            msg = msg.__class__(msgt)
        else:
            msg = msgt
        self.logger.err(msg)