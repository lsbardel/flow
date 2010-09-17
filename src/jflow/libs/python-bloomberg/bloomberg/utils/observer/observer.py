
'''
The observer pattern (sometimes known as publish/subscribe) is a design pattern
used in computer programming to observe the state of an object in a program.
It is related to the principle of implicit invocation.

This pattern is mainly used to implement a distributed event handling system.
In some programming languages, the issues addressed by this pattern are handled
in the native event handling syntax.
This is a very interesting feature in terms of real-time deployment of applications.
The essence of this pattern is that one or more objects (called observers or listeners)
are registered (or register themselves) to observe an event which may be raised by
the observed object (the subject).
(The object which may raise an event generally maintains a collection of the observers.)
http://en.wikipedia.org/wiki/Observer_pattern
'''

__all__ = ['observer','observable','lazyobject']

from datetime import datetime

def get_lock(lock = None):
    from threading import Lock as RLock
    if lock == None:
        return RLock()
    else:
        return lock

## \brief observer base class
#
# This class
class observer(object):
    '''
    This interface defines an updating interface for all observers,
    to receive update notification from the subject.
    The observer class is used as an abstract class to implement concrete observers
    '''
    
    def __new__(cls):
        obj = super(observer,cls).__new__(cls)
        obj.__numupdates = 0
        return obj
        
    def _append_subject(self, subject):
        '''
        Can be implemented by derived classes.
        This function should only be called by the observable class
        '''
        pass
    
    def update(self, args = None):
        '''
        Function called by observables.
        This function should not be overritten by derived classes
        '''
        self.__numupdates += 1
        try:
            return self.doupdate(args)
        except Exception, e:
            pass
        
    def _remove_subject(self, subject):
        '''
        This function should only be called by the observable class
        '''
        pass
        
    def doupdate(self, args=None):
        '''
        Called by update to perform the update on self.
        By default do nothing.
        '''
        return args
    
    def __get_updated(self):
        return self.__numupdates == 0
    updated = property(fget = __get_updated)
    
    def __get_updates(self):
        return self.__numupdates
    updates = property(fget = __get_updates)
    
    def refresh(self):
        '''
        Refresh the observer if needed
        '''
        nup = self.__numupdates
        if nup:
            self.__numupdates = 0
            try:
                self.refresh_me()
            except Exception, e:
                # try to log if possible
                self.__numupdates = nup
                try:
                    self.err(e)
                except:
                    pass
        
    def refresh_me(self):
        '''
        Interface. Implement this method in your observers
        '''
        pass
    
    
class observable(object):
    '''
    observable (or subject) provides an interface for attaching and detaching observers.
    An observable also holds a private list of observers
    '''
    def __new__(cls, *args, **kwargs):
        obj = super(observable,cls).__new__(cls)
        obj.__observers  = []
        obj.__lock       = get_lock(kwargs.pop('lock',None))
        return obj
    
    def __get_lock(self):
        return self.__lock
    lock = property(fget = __get_lock)
    
    def attach(self, obs):
        '''
        attach a new observer
        '''
        if isinstance(obs,observer) and obs is not self:
            if obs not in self.__observers:
                self.__observers.append(obs)
                obs._append_subject(self)
                self.post_attach(obs)
                return True
            else:
                return False
        else:
            return False

    def detach(self, obs):
        if isinstance(obs,observer) and obs is not self:
            try:
                self.__observers.remove(obs)
                obs._remove_subject(self)
            except:
                pass

    def post_attach(self, obs):
        pass
    
    def notify(self, args = None):
        '''
        This is the observable implementation
        '''
        self.__lock.acquire()
        try:
            #if not self.changed: return
            # make a local copy of _observers in case of synchronous additions of observers:
            localArray = self.__observers[:]
            #self.changed = False
        finally:
            self.__lock.release()
        #
        # Updating is not required to be synchronized:
        for ob in localArray:
            ob.update(args)

    def deleteObservers(self):
        self.__observers = []
    
    def __get_countObservers(self):
        return len(self.__observers)
    countObservers = property(fget = __get_countObservers)
    
    def __get_observers(self):
        return self.__observers
    observers = property(fget = __get_observers)


class lazyobject(observable, observer):
    '''
    Lazy object patterns. An object which does calculation on demand.
    It is both a subject and an observer.
    '''
    def __init__(self, *args, **kwargs):
        self.__frozen = kwargs.pop('frozen',False)
        
    def __set_frozen(self, v = True):
        self.__frozen = v
        if not self.__frozen:
            self.notify()
    def __get_frozen(self):
        return self.__frozen
    
    frozen = property(fget = __get_frozen, fset = __set_frozen)
    
    def doupdate(self, args=None):
        '''
        Implementing the observer doupdate method.
        Do not overwrite this method
        put use update_me instead
        '''
        nargs = self.update_me(args)
        self.propagate(nargs)
        return nargs
        
    def propagate(self, args=None):
        '''
        Propagate the update to all observers
        '''
        if not self.frozen:
            self.notify(args)
        
    def update_me(self,args):
        '''
        This method should be implemented by derived classes.
        It update the object when it receves updated from a subject.
        This method is within a lock so that it is thread-safe
        '''
        return args
        

    
