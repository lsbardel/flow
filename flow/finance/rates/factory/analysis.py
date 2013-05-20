from twisted.internet import defer

from jflow.core.timeseries import parsets, tojson, unwind
from jflow.core.rates import cacheObject


__all__ = ['TimeseriesAnalysis']


class jsonResult(object):
    
    def __init__(self, name):
        self.json = {'function': str(name),
                     'success':  True,
                     'result':   None,
                     'error':    None}
        
    def error(self, msg):
        self.json['success'] = False
        self.json['errors']   = msg
        
    def __str__(self):
        f = self.json['function']
        if not self.json['success']:
            er = '-'.join(self.json['errors'])
            return '%s. %s' % (f,er) 
        else:
            return 'Processed %s successfully' % f


class tsloader(defer.Deferred,cacheObject):
    
    def __init__(self, na, holder, start, end, period):
        defer.Deferred.__init__(self)
        self.na                   = na
        self.name                 = str(na)
        holder.loaders[self.name] = self
        self.holder               = holder
        self.loader               = None
        self.result               = None
        
        try:
            self.loader = holder.get_history(self.name,
                                             start  = start,
                                             end    = end,
                                             period = period)
        except Exception, e:
            self.logger.error(e)
            self.get_error('ID "%s" not available' % self.name)
         
    def __str__(self):
        return 'TS loader: %s' % self.name
        
    def get_result(self, res):
        self.na.value = str(self.loader.code())
        self.holder.addresult(self, res)

    def get_error(self, er):
        self.holder.adderror(self, er)


class TimeseriesAnalysis(object):
    '''
    Time series analysis
    '''
    def __init__(self, get_history, cts, start, end, period, observer, json):
        '''
        If json is set to true, the result will be serialized into a JSON object
        '''
        self.cts          = cts
        self.cpars        = None
        self.ids          = {}
        self.loaders      = {}
        self.errs         = []
        self.json         = json
        self.deferred     = defer.Deferred()
        self.get_history  = get_history
        self.start(start, end, period)
    
    def start(self, start, end, period):
        try:
            self.cpars    = parsets(self.cts)
        except Exception, e:
            self.failed(e)
        else:
            names         = self.cpars.names()
            # First create the loaders
            if names:
                for na in names:
                    tsloader(na,self,start,end,period)
            else:
                self.failed('No data Ids in input string')
            # Now add callbacks to the loaders
            for lo in self.loaders.values():
                if lo.loader:
                    lo.loader.addCallback(lo.get_result).addErrback(lo.get_error)
                else:
                    lo.get_error('ID "%s" not available' % lo.name)
                
        
    def __str__(self):
        return "time series Analysis %s" % self.cpars
    
    def __get_errors(self):
        return len(self.errs)
    errors = property(fget = __get_errors)
            
    def lineardecomptest(self):
        cp = self.cpars
        de = cp.lineardecomp()
    
    def adderror(self, loader, er):
        self.loaders.pop(loader.name)
        self.errs.append(str(er))
        if not self.loaders:
            self.failed()
            
    def addresult(self, loader, res):
        self.loaders.pop(loader.name)
        self.ids[str(loader.na)] = res
        if not self.loaders:
            self.finished()
        
    def failed(self, er = None):
        '''
        Failure
        '''
        if er:
            self.errs.append(str(er))
        self.finished()
        
    def finished(self):
        if self.json:
            result = self.__getjson()
        else:
            if self.errors:
                result = self.errors
            else:
                result = unwind(self.cpars, self.ids)
        self.deferred.callback(result)
            
    def __getjson(self):
        result = jsonResult(self.cpars or self.cts)
        if self.errors:
            result.error(self.errors)
        else:
            try:
                ts = tojson(self.cpars, self.ids)
                if not isinstance(ts,list):
                    ts = [ts]
            except Exception, e:
                result.error([str(e)])
            else:
                result.json['result'] = ts
        return result.json
    
    def result(self):
        '''
        return a deferred object for a JSON representation
        of the timeserie analysis
        '''
        return self.deferred.result
            
        
