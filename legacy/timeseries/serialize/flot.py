
import calendar
from jflow.core.dates import qdatetodate
from pyquery import ajax

    
class tsflot(ajax.tsflot):
    
    def __init__(self, **kwargs):
        super(tsflot,self).__init__(**kwargs)
        
    def datatolist(self, ts):
        data = []
        for d,v in ts.items():
            dte = calendar.timegm(qdatetodate(d).timetuple()) * 1000
            data.append([dte,v])
        return data
