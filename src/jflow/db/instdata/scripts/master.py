from jflow.db.geo import country
from jflow.db.instdata.models import IndustryCode, FundType




_blbex = {'Athens': 'ASE',
          'BrsaItaliana': 'BIT',
          'AN Amsterdam': 'ENAM',
          'EN Paris': 'PAR',
          'Hong Kong': 'HKEX',
          'London':'LSE',
          'Korea SE':'KSE',
          'Mexico':'BMV',
          'New York':'NYSE',
          'NASDAQ GS':'NASDAQ',
          'Oslo': 'OSLO',
          'SIX Swiss Ex': 'SIX',
          'Taiwan':'TWSE',
          'Tel Aviv': 'TASE',
          'Tokyo': 'TSE',
          'Toronto':'TSX',
          'Xetra': 'XTA'}

def blbexchanges(code):
    if code:
        c = _blbex.get(code,None)
        if c:
            try:
                return jmodels.Exchange(code = c)
            except:
                return None
        else:
            return None
    else:
        return None




def createsector(id, code, tags = None, **kwargs):
    try:
        c = IndustryCode.objects.get(id = id)
    except:
        try:
            c = IndustryCode(id = id,
                             code = str(code).lower(),
                             **kwargs)
            c.save()
        except:
            return None
    if tags:
        cods = c.code.split(' ')
        for co in cods:
            co.replace(',','')
            if not co:
                continue
            
            co = co.lower()
            if co not in tags:
                if co[-1:] == 's':
                    if co[:-1] not in tags: 
                        tags.append(co)
                else:
                    tags.append(co)
    return c



def getfundtype(ftype, tags = None):
    if not ftype:
        return None
    ftype = str(ftype).upper()
    try:
        ft = FundType.objects.get(code = ftype)
        c = ft.code.lower()
        if tags and c not in tags:
            tags.append(c)
        return ft 
    except:
        return None
    

def tagsfuturecontract(co):
    index = co.index
    typ   = co.type
    if index:
        labels = index.tags.split(' ')
    else:
        labels = []
        
    if typ == 'bond':
        extra = 'bond fixed-income'
    elif typ == 'com':
        extra = 'commodity'
    elif typ == 'eif':
        extra = 'equity index'
    elif typ == 'immirf':
        extra = 'imm interest-rate fixed-income'
    elif typ == 'vif':
        extra = 'volatility'

    extra = '%s future' % extra
    extra = extra.split(' ')
    for l in extra:
        if l not in labels:
            labels.append(l)
    return ' '.join(labels)
