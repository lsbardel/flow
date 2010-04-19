from datetime import date

from ccy.tradingcentres import centres

from jflow.conf import settings

from converter import get_date

tcs = centres(settings.DEFAULT_TRADING_CENTRES)


def get_livedate(dte):
    if isinstance(dte,livedate):
        return dte
    else:
        return livedate(get_date(dte))


class livedate(object):
    '''
    Utility class for financial dates
    '''
    def __init__(self, dte = None):
        self.live   = True
        self.__date = None
        if isinstance(dte,date):
            if dte < date.today():
                self.live   = False
                self.__date = tcs.prevbizday(dte,0)
    
    def __repr__(self):
        if self.live:
            return 'live'
        else:
            return str(self.date)
        
    def __str__(self):
        return self.__repr__()
    
    def __unicode__(self):
        return u'%s' % self.__repr__()
    
    def __get_date(self):
        if self.live:
            import datetime
            return datetime.datetime.now()
        else:
            return self.__date
    date = property(fget = __get_date)
    
    def __get_dateonly(self):
        if self.live:
            import datetime
            return datetime.date.today()
        else:
            return self.__date
    dateonly = property(fget = __get_dateonly)
    
    def __eq__(self, dte):
        try:
            if self.live:
                return dte.live
            else:
                return self.date == dte.date
        except:
            return False
        
    def __ne__(self, dte):
        return not self == dte
    
    def __gt__(self, dte):
        try:
            if dte.live:
                return False
            elif self.live:
                return True
            else:
                return self.date > dte.date
        except:
            return False
        
    def __lt__(self, dte):
        try:
            if self.live:
                return False
            elif dte.live:
                return True
            else:
                return self.date < dte.date
        except:
            return False
        
    def __ge__(self, dte):
        return not self < dte
    
    def __le__(self, dte):
        return not self > dte