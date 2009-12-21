"""
A pool of threads to which we dispatch tasks.

Adapted from twisted.python.threadpool
"""

# System Imports
import Queue
import threading
import copy
import sys
import warnings


# Twisted Imports
from twisted.python import log, runtime, context, threadable

WorkerStop = object()

__all__ = ['WorkerThread',
           'WorkRequest',
           'ThreadPool']


# exceptions
class NoResultsPending(Exception):
    """All work requests have been processed."""
    pass

class NoWorkersAvailable(Exception):
    """No worker threads available to process remaining requests."""
    pass


# internal module helper functions
def _handle_thread_exception(request, exc_info):
    """Default exception handler callback function.

    This just prints the exception info via ``traceback.print_exception``.

    """
    traceback.print_exception(*exc_info)



class WorkRequest:
    """A request to execute a callable for putting in the request queue later.

    See the module function ``makeRequests`` for the common case
    where you want to build several ``WorkRequest`` objects for the same
    callable but with different arguments for each call.

    """

    def __init__(self, callable_, args=None, kwds=None, requestID=None,
            callback=None, exc_callback=_handle_thread_exception):
        """Create a work request for a callable and attach callbacks.

        A work request consists of the a callable to be executed by a
        worker thread, a list of positional arguments, a dictionary
        of keyword arguments.

        A ``callback`` function can be specified, that is called when the
        results of the request are picked up from the result queue. It must
        accept two anonymous arguments, the ``WorkRequest`` object and the
        results of the callable, in that order. If you want to pass additional
        information to the callback, just stick it on the request object.

        You can also give custom callback for when an exception occurs with
        the ``exc_callback`` keyword parameter. It should also accept two
        anonymous arguments, the ``WorkRequest`` and a tuple with the exception
        details as returned by ``sys.exc_info()``. The default implementation
        of this callback just prints the exception info via
        ``traceback.print_exception``. If you want no exception handler
        callback, just pass in ``None``.

        ``requestID``, if given, must be hashable since it is used by
        ``ThreadPool`` object to store the results of that work request in a
        dictionary. It defaults to the return value of ``id(self)``.

        """
        if requestID is None:
            self.requestID = id(self)
        else:
            try:
                self.requestID = hash(requestID)
            except TypeError:
                raise TypeError("requestID must be hashable.")
        self.ctx       = context.theContextTracker.currentContext().contexts[-1]
        self.exception = False
        self.callback  = callback
        self.exc_callback = exc_callback
        self.callable = callable_
        self.args = args or []
        self.kwds = kwds or {}

    def __str__(self):
        return "<WorkRequest id=%s args=%r kwargs=%r exception=%s>" % \
            (self.requestID, self.args, self.kwds, self.exception)
            


class WorkerThread(threading.Thread):
    """Background thread connected to the requests/results queues.

    A worker thread sits in the background and picks up work requests from
    one queue and puts the results in another until it is dismissed.

    """

    def __init__(self, pool, **kwds):
        """Set up thread in daemonic mode and start it immediatedly.

        ``requests_queue`` and ``results_queue`` are instances of
        ``Queue.Queue`` passed by the ``ThreadPool`` class when it creates a new
        worker thread.

        """
        threading.Thread.__init__(self, **kwds)
        self._pool = pool
        self.setDaemon(1)
        self._dismissed      = threading.Event()
        self.start()
        a = 1

    def run(self):
        '''
        Repeatedly process the job queue until told to exit.
        '''
        pool = self._pool
        q    = pool.q
        while True:
            if self._dismissed.isSet():
                # we are dismissed, break out of loop
                break
            # get next work request. If we don't get a new request from the
            # queue after self._poll_timout seconds, we jump to the start of
            # the while loop again, to give the thread a chance to exit.
            try:
                request = q.get(True, pool.timeout)
            except Queue.Empty:
                # Nothing in the queue, check with the thread pool if I can be dismissed
                pool.dropifpossible(self)
                continue
            except:
                #Somethig else append. Lets get out
                break
            else:
                if self._dismissed.isSet():
                    # we are dismissed, put back request in queue and exit loop
                    q.put(request)
                    break
                try:
                    result = request.callable(*request.args, **request.kwds)
                    #self._results_queue.put((request, result))
                except:
                    request.exception = True
                    #self._results_queue.put((request, sys.exc_info()))
                pool.waiters.pop(request.requestID)
                    
        pool.threads.remove(self)

    def dismiss(self):
        """Sets a flag to tell the thread to exit when done with current job."""
        self._dismissed.set()



class ThreadPool(object):
    """
    This class (hopefully) generalizes the functionality of a pool of
    threads to which work can be dispatched.

    callInThread() and stop() should only be called from
    a single thread, unless you make a subclass where stop() and
    _startSomeWorkers() are synchronized.
    """

    #threadFactory = threading.Thread
    threadFactory = WorkerThread
    currentThread = staticmethod(threading.currentThread)

    def __init__(self, minthreads=1, maxthreads=5, name=None, q_size=0, timeout = 5):
        """
        Create a new threadpool.

        @param minthreads: minimum number of threads in the pool

        @param maxthreads: maximum number of threads in the pool
        
        @param timeout:  waiting time on the queue
        """
        try:
            minthreads = int(minthreads)
        except:
            minthreads = 0
        try:
            maxthreads = int(maxthreads)
        except:
            maxthreads = minthreads
        minthreads = max(minthreads,0)
        maxthreads = max(minthreads,maxthreads)
        
        self.timeout = max(timeout, 1)
        self.q     = Queue.Queue(q_size)
        self.min   = minthreads
        self.max   = maxthreads
        self.name  = name
        self.waiters = {}
        self.threads = []
        self.working = []
        self.joined  = False
        self.started = False
        self.start()
        
    def __str__(self):
        return "PoolThread %s" % self.name or id(self)

    def __repr__(self):
        return self.__str__()
    
    def __get_workers(self):
        return len(self.threads)
    workers = property(fget = __get_workers)

    def start(self):
        """
        Start the threadpool.
        """
        if self.started or self.joined:
            return
        self.started = True
        
        while self.workers < self.min:
            self.startAWorker()

    def startAWorker(self):
        workers = self.workers
        if workers < self.max:
            name = "PoolThread-%s-%s" % (self.name or id(self), workers+1)
            newThread = self.threadFactory(self, name=name)
            self.threads.append(newThread)

    def dropifpossible(self, worker):
        if self.workers > self.min and worker in self.threads:
            worker.dismiss()
            
    def stopAWorker(self, worker = None):
        if self.workers:
            w = self.threads.pop()
            w.dismiss()

    def _startSomeWorkers(self):
        neededSize = self.q.qsize() + len(self.working)
        while self.workers < min(self.max, neededSize):
            self.startAWorker()
            
    def putRequest(self, request, block=True, timeout=0):
        '''
        Put work request into work queue and save its id for later.
        '''
        if isinstance(request, WorkRequest) and not getattr(request, 'exception', None):
            self.q.put(request, block, timeout)
            self.waiters[request.requestID] = request

    def callInThread(self, func, *args, **kw):
        '''
        Dispatch a function to be a run in a thread.
        '''
        if self.joined:
            return
        request = WorkRequest(func, args, kw)
        self.putRequest(request)
        if self.started:
            self._startSomeWorkers()
            
    def deferToThread(self, callback, errback, func, *args, **kw):
        """
        Dispatch a function, returning the result to a callback function.

        The callback function will be called in the thread - make sure it is thread-safe.
        """
        self.callInThread(self._runWithCallback, callback, errback, func, args, kw)

    def _runWithCallback(self, callback, errback, func, args, kwargs):
        try:
            result = apply(func, args, kwargs)
        except Exception, e:
            errback(sys.exc_info()[1])
        else:
            callback(result)

    def stop(self):
        """
        Shutdown the threads in the threadpool.
        """
        log.msg('%s - Stopping al workers' % self)
        self.joined = True
        threads = copy.copy(self.threads)
        for w in threads:
            w.dismiss()

    def dumpStats(self):
        log.msg('queue: %s'   % self.q.queue)
        log.msg('waiters: %s' % self.waiters)
        log.msg('workers: %s' % self.working)
        log.msg('total: %s'   % self.threads)
        
        


if __name__ == '__main__':
    import random
    import time

    # the work the threads will have to do (rather trivial in our example)
    def do_something(data):
        t = threading.currentThread()
        time.sleep(random.randint(1,5))
        res = round(random.random() * d, 5)
        print 'From thread %s -> random result %s' % (t.name,res)

    # assemble the arguments for each job to a list...
    data = [random.randint(1,10) for i in range(20)]

    # we create a pool of 3 worker threads
    print "Creating thread pool with 1 to 3 worker threads."
    main = ThreadPool(minthreads = 1, maxthreads = 3, name = 'Test drive')
    
    for d in data:
        main.callInThread(do_something, d)
    
    while True:
        print 'Pool thread has %s threads' % main.workers
        time.sleep(0.5)

    