
def equity(**kwargs):
    from jflow.core import finins as FININS
    return FININS.equity(**kwargs)

def bond(**kwargs):
    from jflow.core import finins as FININS
    return FININS.BulletBond(**kwargs)

def cash(**kwargs):
    from jflow.core import finins as FININS
    return FININS.CashInst(**kwargs)

def forex(**kwargs):
    from jflow.core import finins as FININS
    pair = inst.pair
    return FININS.fwdfx(pair = pair, inst = inst, **kwargs)

def warrant(**kwargs):
    from jflow.core import finins as FININS
    return FININS.equity(**kwargs)


def future(inst = None, **kwargs):
    from jflow.core import finins as FININS
    '''
    Create a future instrument
    '''
    ftype = inst.contract.type
    if ftype == 'immirf':
        ccy = inst.ccy()
        dc  = ccy.floatdc
        return FININS.immIrFuture(dc = dc, inst = inst, **kwargs)
    #
    elif ftype == 'bond':
        return FININS.bondfuture(inst = inst, **kwargs)
    #
    else:
        return FININS.future(inst = inst, **kwargs)



   
    