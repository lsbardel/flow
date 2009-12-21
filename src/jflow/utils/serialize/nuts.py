
def iterable_no_string(obj):
    t = type(obj)
    if t == str or t == unicode:
        return False
    else:
        return iterable(obj)

def iterable(obj):
    try:
        for i in obj:
            return True
    except:
        return False
    
    
def isnumeric(obj):
    '''
    Return true if obj is a numeric value
    '''
    from decimal import Decimal
    if type(obj) == Decimal:
        return True
    else:
        try:
            float(obj)
        except:
            return False
        return True
    
def json_number(obj):
    from decimal import Decimal
    typ = type(obj)
    if typ == Decimal:
        return float(str(obj))
    else:
        return obj

def json_value(v):
    typ = type(v)
    if v == None or typ == str or typ == unicode:
        return v
    elif isnumeric(v):
        return json_number(v)
    elif iterable(v):
        return v
    else:
        return str(v)
    