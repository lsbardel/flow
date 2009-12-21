


def lazyattr(f):
    
    def wrapper(obj, *args, **kwargs):
        name = 'lazy_%s' % f.__name__
        try:
            return getattr(obj,name)
        except:
            v = f(obj, *args, **kwargs)
            setattr(obj,name,v)
            return v
    return wrapper


def threadSafe(f):
    '''
    Make a method of object 'obj' thread safe.
    'obj' must have a lock object
    '''
    def wrapper(obj, *args, **kwargs):
        obj.lock.acquire()
        try:
            return f(obj, *args, **kwargs)
        finally:
            obj.lock.release()
    return wrapper
    
    
def runInThread(f):
    from jflow.utils import tx
    return tx.runInThread(f)