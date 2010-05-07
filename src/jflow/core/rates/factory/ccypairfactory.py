
from factory import compositeFactory


class ccypairFactory(compositeFactory):
    
    def __init__(self, c1, c2):
        if str(c1) == 'USD':
            codes = (c2,)
        elif str(c2) == 'USD':
            codes = (c1,)
        else:
            codes = (c1,c2)
        super(ccypairFactory,self).__init__(True,*codes)
        self.c1 = c1
        self.c2 = c2
        
    def code(self):
        return '%s%s' % (self.c1,self.c2)
    
    def buildcomposite(self, cts, tseries):
        if str(self.c1) == 'USD':
            c1 = None
            c2 = tseries.get(str(self.c2))
            if c2:
                self._buildc2(cts,c2)
        elif str(self.c2) == 'USD':
            c1 = tseries.get(str(self.c1))
            if c1:
                self._buildc1(cts,c1)
        else:
            c1 = tseries.get(str(self.c1))
            c2 = tseries.get(str(self.c2))
            if c1 and c2:
                self._buildc12(cts,c1,c2)
        
    def _buildc1(self, cts, c1):
        func = self.c1.overusdfunc()
        for k,v in c1.items():
            cts[k] = func(v) 
    
    def _buildc2(self, cts, c2):
        func = self.c2.usdoverfunc()
        for k,v in c2.items():
            cts[k] = func(v)
    
    def _buildc12(self, cts, c1, c2):
        func1 = self.c1.overusdfunc()
        func2 = self.c2.usdoverfunc()
        for k,v1 in c1.items():
            try:
                v2 = c2[k]
                cts[k]  = func1(v1) * func2(v2)
            except:
                pass
