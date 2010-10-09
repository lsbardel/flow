

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