import time

from twisted.internet import defer
from twisted.internet import threads

from jflow.utils.decorators import threadSafe
from jflow.utils.serialize import baseArgs, errorArg, Result


__all__ = ['isdefer',
           'syncr',
           'wrapResult',
           'runInThread',
           'threadSafeInThread',
           'runInMainThread',
           'postTwistedEvent',
           'safeCallWrapper']

def isdefer(d):
    return isinstance(d,defer.Deferred)


def syncr(f):
    
    def wrapper(*args, **kwargs):
        result = None
        def done(res):
            result = res
        f(*args,**kwargs).addBoth(done)
        while not result:
            time.sleep(0.1)
        return result


def wrapResult(f):
    
    def wrapper(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
            if isinstance(r,baseArgs):
                return r
            else:
                return Result(result = r)
        except Exception, e:
            return errorArg(error = e)

    return wrapper

     
def runInThread(f):
    '''
    Decorator which run a member function in a separate twisted thread.
    It returns a twisted.internet.defer object
    '''
    def wrapper(*args, **kwargs):
        from twisted.internet import reactor
        def crun(d):
            r  = f(*args, **kwargs)
            if isdefer(r):
                r.addCallback(d.callback)
            else:
                d.callback(r)
        d = defer.Deferred()
        reactor.callInThread(crun,d)
        return d
    
    return wrapper

def threadSafeInThread(f):
    return runInThread(threadSafe(f))


def runInMainThread(f):
    '''
    Decorator which run a member function in a separate twisted thread.
    It returns a twisted.internet.defer object
    '''
    def wrapper(*args, **kwargs):
        from twisted.internet import reactor
        def crun(d):
            r  = f(*args, **kwargs)
            if isdefer(r):
                r.addCallback(d.callback)
            else:
                d.callback(r)
        d = defer.Deferred()
        reactor.callFromThread(crun,d)
        return d
    
    return wrapper


def postTwistedEvent(f):
    
    def wrapper(req, *args, **kwargs):
        
        def crun():
            return f(req, *args, **kwargs)
        
        con = req.connection
        if not con:
            raise ValueError, 'No connection handler available'
        req.incall = True
        tm = con.twistedManager
        if tm:
            return tm(crun)
        else:
            return crun()
        
    return  wrapper


def safeCallWrapper(f):
    '''
        Decorator
        1 - Unpickle the arguments
        2 - Create the observer for handling remote updates
        3 - Wrap the function within an try-except block
        4 - Make sure the remote observer receive an update
    '''
    def wrapper(obj, args):
        from lazy import create_observer, new_args
        from base import decode_remote_data
        observer = None
        try:
            remote   = args[0]
            arg      = decode_remote_data(args[1])
            observer = create_observer(remote, arg)
            res = f(obj, new_args(remote, arg, observer))
        except Exception, e:
            if observer:
                r = errorArg(error = e)
                observer.update(r)
                
    return wrapper