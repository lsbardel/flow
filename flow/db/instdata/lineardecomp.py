'''
Linear decomposition of an financial security
'''
from jflow.db.geo import currency, countryccy



class linearAtom(object):
    
    def __init__(self, delta, ccy, undccy, und):
        self.delta      = delta
        self.ccy        = ccy
        self.undccy     = undccy
        self.underlying = und
        self.valid      = True
        
    def __str__(self):
        return '%s * %s * %s' % (self.delta, self.ccy, self.underlying.code)
    
    def __repr__(self):
        return self.__str__()

class badAtom(linearAtom):
    
    def __init__(self, *args):
        super(badAtom,self).__init__(*args)
        self.valid      = False
        
    def __str__(self):
        return '%s * %s * %s' % (self.delta, self.ccy, self.underlying)


class LinearDecomp(object):
    separator1 = ','
    separator2 = '*'
    
    def __init__(self, data = None):
        self.errors = []
        self.data   = ''
        if data:
            self.data = str(data).replace(' ','').upper()
            try:
                self.deco = self.__decompose()
            except:
                self.deco = []
        else:
            self.deco = []
    
    def __get_valid(self):
        if not self:
            return False
        if not self.delta:
            return False
        for d in self:
            if not d.valid:
                return False
        return True
    valid = property(fget = __get_valid)
    
    def __len__(self):
        return len(self.deco)
    
    def __iter__(self):
        return self.deco.__iter__()   
    
    def __str__(self):
        return str(self.deco)
    
    def __get_delta(self):
        td = 0.0
        for d in self:
            td += d.delta
        return td
    delta = property(fget = __get_delta)
    
    def __decompose(self):
        cs = self.data.split(self.separator1)
        deco = []
        for c in cs:
            comp = c.split(self.separator2)
            N     = len(comp)
            delta = 1
            ccy     = None
            und     = None
            undcode = None
            
            if N == 3:
                delta = self._safe_delta(comp[0])
                if delta == None:
                    self.errors.append(c)
                    continue
                ccy, undcode = self.get_ccy_und(comp[1:])
            elif N == 2:
                delta = self._safe_delta(comp[0])
                if delta == None:
                    delta = 1
                else:
                    comp = comp[1:]
                ccy, undcode = self.get_ccy_und(comp)
            elif N == 1:
                undcode = comp[0]
            else:
                raise ValueError('could not understand decomposition %s' % self.data)
                
            try:
                und   = self.underlying(undcode)
            except:
                deco.append(badAtom(delta,ccy,ccy,undcode))
            else:
                undccy = countryccy(und.country)
                if ccy == None:
                    ccy = undccy
                if ccy == None:
                    deco.append(badAtom(delta,ccy,ccy,undcode))
                else:
                    deco.append(linearAtom(delta,ccy,undccy,und))
                    
        return deco
    
    def get_ccy_und(self, comp):
        N = len(comp)
        if N==2:
            try:
                ccy   = self.currency(comp[0])
                undcode = comp[1]
            except:
                ccy   = self.currency(comp[1])
                undcode = comp[0]
            return ccy,undcode
        elif N==1:
            return None, comp[0]
        else:
            return None, None
            
    def _safe_delta(self, val):
        try:
            return float(val)
        except:
            return None
        
    def currency(self, val):
        ccy = currency(val)
        if ccy == None:
            raise ValueError
        else:
            return ccy
    
    def underlying(self, val):
        from models import DataId
        code = val.upper()
        return DataId.objects.get(code = code)
        

    