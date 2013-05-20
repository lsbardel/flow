from portfolio import FinIns

__all__ = ['equity','etf']

class equity(FinIns):
    
    def price_to_value(self, price, size, dt = None):
        return size*self.multiplier*price
    
    def pv01(self, size = 1.0, price = 0, dt = None):
        return 0.01*self.price_to_value(price, size, dt)
    
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
        