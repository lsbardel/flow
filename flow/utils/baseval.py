from decimal import Decimal

def baseval(obj):
    '''
    Return true if obj is a numeric value
    '''
    if obj == None:
        return None
    if isinstance(obj,bool) or isinstance(obj,str) or isinstance(obj,unicode) or isinstance(obj,list) or isinstance(obj,dict):
        return obj
    elif isinstance(obj,Decimal):
        return float(str(obj))
    else:
        try:
            return float(obj)
        except:
            return str(obj)
    

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