from portfolio import FinIns

__all__ = ['equity','etf']

class equity(FinIns):
    
    def pv01(self, size = 1.0):
        return 0.01*size*self.multiplier*self.price()
    
    def notional(self, size = 1.0):
        try:
            p = float(self.mktprice)
            return self.multiplier()*size*p
        except:
            return self.notavailable
    
    def nav(self, size):
        return self.notional(size)
        
        
        
class etf(equity):
    pass
        