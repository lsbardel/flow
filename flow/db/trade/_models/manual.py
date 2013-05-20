from base import *
from trade import Fund
from manip import Position

__all__ = ['ManualTrade']

class ManualTrade(TimeStamp):
    user            = models.ForeignKey(User)
    quantity        = models.DecimalField(default = 0, max_digits=MAX_DIGITS,decimal_places = ROUNDING)
    portfolio       = models.ForeignKey(Fund)
    open_date       = models.DateField()
    close_date      = models.DateField(null = True, blank = True)
    price           = models.FloatField(default = 0)
    position        = models.ForeignKey(Position, blank = True)
    comment         = models.TextField()
    
    class Meta:
        app_label    = current_app_label
        
    def __get_instrumentCode(self):
        return self.position.instrumentCode
    instrumentCode = property(fget = __get_instrumentCode)
    
    def __unicode__(self):
        return u'%s (%s)' % (self.instrumentCode,self.open_date)
    
    