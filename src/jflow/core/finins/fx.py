
from base import fxins, value_date_plugin, dates


class fwdfx(fxins, value_date_plugin):
    
    def __init__(self, value_date = None, pair = None, *args, **kwargs):
        value_date_plugin.__init__(self, value_date)
        code = '%s vd %s' % (pair, self.value_date.strftime('%d %b %Y'))
        fxins.__init__(self, pair = pair, code = code, *args, **kwargs)
        
    def _code(self):
        return 
        
    def end_date(self):
        return self.value_date 
        
    