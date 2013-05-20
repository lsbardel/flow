from portfolio import FinIns

#class future(finins, future_instrument):
class future(FinIns):
    
    def __init__(self, *args, **kwargs):
        super(FinIns,self).__init__(self, *args, **kwargs)
        
    def nav(self, size = 1):
        return 0
    
    def notional(self, size = 1):
        try:
            p = float(self.mktprice)
            return p*float(self.dbinstrument.tonotional(size))
        except:
            return self.notavailable

    