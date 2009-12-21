from jflow.core.pricers import Pricer

class CashPricer(Pricer):
    
    def __init__(self):
        super(CashPricer,self).__init__()
        
    def calculate(self, inst, args):
        pass
        
        
class FwdPricer(CashPricer):
    
    def __init__(self):
        super(FwdPricer,self).__init__()
        
        
class DepoPricer(CashPricer):
    
    def __init__(self):
        super(DepoPricer,self).__init__()
        