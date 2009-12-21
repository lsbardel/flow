


from base import finins, future_instrument

future_month_list = ['F','G','H','J','K','M','N','Q','U','V','X','Z']
short_month = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
short_to_number = {}
c = 0

for i in short_month:
    c += 1
    short_to_number[i] = c
    
def date_to_code(dte):
    return '%s%s' % (future_month_list[dte.month-1],str(dte.year)[2:])

def monthDictionary():
    global future_month_list, short_month
    di = {}
    for i in range(0,12):
        c = future_month_list[i]
        s = short_month[i]
        di[c] = (i+1,s)
    return di

future_month_dict = monthDictionary()



class future(finins, future_instrument):
    
    def __init__(self, *args, **kwargs):
        finins.__init__(self, *args, **kwargs)
        
    def nav(self, size = 1):
        return 0
    
    def notional(self, size = 1):
        try:
            p = float(self.mktprice)
            return p*float(self.dbinstrument.tonotional(size))
        except:
            return self.notavailable

    