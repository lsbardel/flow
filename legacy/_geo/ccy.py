from jflow.utils.dblite import objdb


class ccy(object):
    '''
    Currency object
    '''
    def __init__(self, code, isonumber, twolettercode, order, name, 
                 fixeddc   = None,
                 floatdc   = None,
                 fixedfreq = None,
                 floatfreq = None,
                 future    = None):
        #from qmpy.finance.dates import get_daycount
        self.code          = str(code)
        self.isonumber     = isonumber
        self.twolettercode = str(twolettercode)
        self.order         = int(order)
        self.name          = str(name)
        #self.fixeddc       = get_daycount(fixeddc)    
        #self.floatdc       = get_daycount(floatdc)
        #self.fixedfreq     = str(fixedfreq)
        #self.floatfreq     = str(floatfreq)
        self.future        = ''
        if future:
            self.future    = str(future)
        
    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__,self.code)
    
    def __str__(self):
        return self.code
    
class ccypair(object):
    '''
    Currency pair object
    '''
    def __init__(self, c1, c2):
        self.ccy1 = c1
        self.ccy2 = c2
        self.code = '%s%s' % (c1,c2)
    
    def __repr__(self):
        return '%s: %s' (self.__class__.__name__,self.code)
    
    def __str__(self):
        return self.code
    
    
def make_ccys():
    fields = ['code',
              'isonumber',
              'twolettercode',
              'order',
              'name']
    db = objdb(name   = 'currencies',
               pk     = 'code',
               fields = fields)
    
    db.insert(ccy('EUR','978','EU',1, 'Euro'))
    db.insert(ccy('GBP','826','BP',2, 'British Pound'))
    db.insert(ccy('AUD','036','AD',3, 'Australian Dollar'))
    db.insert(ccy('NZD','554','ND',4, 'New-Zealand Dollar'))
    db.insert(ccy('USD','840','UD',5, 'US Dollar'))
    db.insert(ccy('CAD','124','CD',6, 'Canadian Dollar'))
    db.insert(ccy('CHF','756','SF',7, 'Swiss Franc'))
    db.insert(ccy('NOK','578','NK',8, 'Norwegian Krona'))
    db.insert(ccy('SEK','752','SK',9, 'Swedish Krona'))
    db.insert(ccy('DKK','208','DK',10, 'Danish Krona'))
    db.insert(ccy('JPY','392','JY',1000,'Japanese Yen'))
    
    db.insert(ccy('KRW','410','KW',14,'South Korean won'))
    db.insert(ccy('SGD','702','SD',15,'Singapore Dollar'))
    db.insert(ccy('IDR','360','IH',16,'Indonesian Rupiah'))
    db.insert(ccy('THB','764','TB',17,'Thai Baht'))
    db.insert(ccy('TWD','901','TD',18,'Taiwan Dollar'))
    db.insert(ccy('HKD','344','HD',19,'Hong Kong Dollar'))
    
    db.insert(ccy('BRL','986','BC',21,'Brazilian Real'))
    db.insert(ccy('MXN','484','MP',22,'Mexican Peso'))
    
    db.insert(ccy('CZK','203','CK',28,'Czech Koruna'))
    db.insert(ccy('PLN','985','PZ',29,'Polish Zloty'))
    db.insert(ccy('TRY','949','TY',30,'Turkish Lira'))
    db.insert(ccy('HUF','348','HF',32,'Hungarian Forint'))
    db.insert(ccy('RON','946','RN',34,'Romanian Leu'))
    db.insert(ccy('RUB','643','RR',36,'Russian Ruble'))
    
    db.insert(ccy('ILS','376','IS',41,'Israeli Shekel'))
    db.insert(ccy('ZAR','710','SA',43,'South African Rand'))
    return db


def make_ccy_pairs(ccys):
    fields = ['code',
              'ccy1',
              'ccy2']
    db = objdb(name   = 'ccypairs',
               pk     = 'code',
               fields = fields)
    
    for ccy1 in ccys:
        od = ccy1.get('order')
        for ccy2 in ccys:
            if ccy2.get('order') <= od:
                continue
            p = ccypair(ccy1.data,ccy2.data)
            db.insert(p)
    return db
            