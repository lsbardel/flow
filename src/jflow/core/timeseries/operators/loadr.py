
_rlibs = ['PerformanceAnalytics',
          'quantmod']

import rpy2.robjects

def robject():
    global _robj, _rlibs
    
    if not _robj:
        r = rpy2.robjects.r   
    
        for lib in _rlibs:
            r('library(%s)' % lib)
    
        _robj = r
        
    return _robj


_robj = None