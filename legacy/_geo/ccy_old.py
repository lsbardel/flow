

__all__ = ['currency',
           'currency_tuples',
           'currencydb',
           'ccypair',
           'currency_pair_tuples']
    

def currency(code):
    ccys = currencydb()
    return ccys.get(code = str(code).upper())

def ccypair(code):
    ccys = ccypairsdb()
    return ccys.get(code = str(code).upper())

def currency_tuples():
    ccys = currencydb()
    cs = []
    for c in ccys:
        cs.append((c.id,c.id))
    return cs

def currency_pair_tuples():
    ccys = ccypairsdb()
    cs = []
    for c in ccys:
        cs.append((c.id,c.id))
    return cs
    
def ccypairsdb():
    global _ccypairs
    if not _ccypairs:
        import _geo 
        ccys = currencydb()
        _ccypairs = _geo.make_ccy_pairs(ccys)
    return _ccypairs

def currencydb():
    global _ccys
    if not _ccys:
        import _geo
        _ccys = _geo.make_ccys()
    return _ccys
    


_ccys = None
_ccypairs = None



if __name__ == '__main__':
    c = currency('eur')