
from jflow.db.instdata.models import TrimCode, Vendor
from jflow.db.instdata.fields import fieldproxy, premium, intravol

default_field = fieldproxy('LAST_PRICE')

fields_shortcuts = {'ASK' :'ASK_PRICE',
                    'BID' :'BID_PRICE',
                    'LOW' :'LOW_PRICE',
                    'HIGH':'HIGH_PRICE',
                    'OPEN':'OPEN_PRICE',
                    'PREM':premium('PREM'),
                    'INTRAVOL':intravol('INTRAVOL')}

def get_field(field = None):
    '''
    Return a valid field proxy object
    '''
    if isinstance(field,fieldproxy):
        return field
        
    if field == None:
        return default_field
    else:
        fc  = TrimCode(field)
        nfc = fields_shortcuts.get(fc,None)
        if isinstance(nfc,fieldproxy):
            return nfc
            
        if nfc:
            fc = nfc
                
        try:
            fdb = DataField.objects.get(code = fc)
            return fieldproxy(fc)
        except:
            return default_field
        

def get_vendor(vendor):
    if vendor:
        try:
            Vendor.objects.get(str(vendor).lower())
        except:
            return None
    else:
        return None