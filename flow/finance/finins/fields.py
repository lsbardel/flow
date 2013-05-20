

__all__ = ['finfields']

def fstring(name, d):
    return 

formatters = ('string','number','currency','percentage','date')

class Fields(object):
    
    def __init__(self):
        self.fields = {}

    def fstring(self, name):
        self.fields[name] = 'string'
        
    def fnumber(self, name):
        self.fields[name] = 'number'
        
    def fcurrency(self, name):
        self.fields[name] = 'currency'
        
    def fpercentage(self, name):
        self.fields[name] = 'percentage'
        
    def fdate(self, name):
        self.fields[name] = 'date'

_f = Fields()


_f.fstring('id')
_f.fstring('code')
_f.fstring('name')
_f.fstring('ccy')

_f.fnumber('price')

_f.fpercentage('volatility')

_f.fcurrency('notional')
_f.fcurrency('nav')


finfields = _f.fields
