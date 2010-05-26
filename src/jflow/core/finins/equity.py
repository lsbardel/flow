from portfolio import FinIns

__all__ = ['equity']

class equity(FinIns):
    
    def pv01(self):
        m = self.multiplier()
        return 0.01*m*self.price()*self.size()
    
    def notional(self, size = 1):
        try:
            p = float(self.mktprice)
            return self.multiplier()*size*p
        except:
            return self.notavailable
    
    def nav(self, size):
        return self.notional(size)
        
        