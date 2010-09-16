'''Contains operators for joint timeseries'''

from baseoper import tsoperator
from jflow.core.dates import converter
import numpy as np
import rpy2.robjects.numpy2ri
import rpy2.robjects as robject

from roll import rSingleTS

class covvar(rSingleTS):
    ''' Returns the rolling covariance variance values for ids
        If window = none it returns a single value for the whole period        
    '''
    def __init__(self):
        super(covvar,self).__init__()
        self.rFunc = self.r['cor']        
    
    def _roll_apply(self,window,args):
        #Called when a window value is passed
        
        zoo_merge = []
        for ts in args:
            zoo_ts_tmp = self.tsToZoo(ts) #Zoo object matching the dataseries
          
            if not zoo_merge:
                zoo_merge = zoo_ts_tmp
            else:
                zoo_merge = self.r['merge'](zoo_merge,zoo_ts_tmp)            
        
        _result_tmp = self.rFunc(zoo_merge)
        for i in _result_tmp:
            print i
        
        _result =self.rApplyFunc(zoo_merge,window,self.rFunc,align = "center")
        
        ns = self.zooToTs(_result)        
        
        return self.unwind.tsData(data = ns)
        
        
    
    def apply(self, *args, **kwargs):
        window = kwargs.pop('window',None)   
        
        return self._roll_apply(window,args)