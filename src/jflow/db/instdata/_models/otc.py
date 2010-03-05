
from instrument import NoDataInstrumentBase



class OTCIR(NoDataInstrumentBase):
    curncy = models.CharField(max_length=3,choices=geo.currency_tuples(),verbose_name="currency")
    maturity = models.DateField()
    
    def name(self):
        return self.description()
    
    def description(self):
        return 'cash %s' % cash_type_dict.get(self.type,'').lower()
    
    class Meta:
        abstract = True
        
    def ccy(self):
        return self.curncy
        
    def make_position(self, **kwargs):
        return FACTORY.cash(inst = self, **kwargs)
    