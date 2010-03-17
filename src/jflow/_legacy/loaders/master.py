from jflow.db.geo import country
from jflow.db.instdata.models import IndustryCode, FundType, BondMaturityType


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


def maturityType(call,put,conv,mat):
    get = BondMaturityType.objects.get
    if call:
        if put:
            return get(code = 'CALLPUT')
        elif not mat:
            return get(code = 'PERPCALL')
        else:
            return get(code = 'CALLABLE')
    elif put:
        return get(code = 'PUTABLE')
    elif conv:
        return get(code = 'CONVERTIBLE')
    elif not mat:
        return get(code = 'PERPETUAL')
    else:
        return get(code = 'BULLET')