from jflow.db.instdata.models import Cash

def makecode(obj):
    '''
    Create a code for cash instrument
    '''
    ci = obj.codeinfo()
    if ci:
        typ = ci['code']
    else:
        typ = 'UNK'
    return '%sCASH%s' % (obj.curncy,typ)


def renamecash():
    for obj in Cash.objects.all():
        ic = obj.code
        code = makecode(obj)
        ic.code = code
        ic.firm_code = code
        ic.save() 