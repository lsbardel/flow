from django.db import models
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist

from jflow.db import geo
from jflow.db.utils import django_choices, dict_from_choices
from jflow.utils.decorators import lazyattr

from jflow.conf import settings

#from jflow.core.dates import DateFromString

current_app_label = 'instdata'

Future_Price_Types = (('PRICE','Price'),
                      ('BILL','Bill'),
                      ('RATE','Rate')
                     )

Exercise_Types = ((1,'European'),
                  (2,'American'),
                  (3,'Bermudan')
                  )

Settle_Types = ((1,'Physical'),
                (2,'Cash')
                )

field_type = (('numeric','Numeric'),
              ('string','String'),
              ('date','Date'))

equity_type = ((1,'Common Stock'),
               (2,'Right')
               )

future_type_choice = (
                      ('bond','Bond Future'),
                      ('com','Commodity Future'),
                      ('immirf','IMM Interest Rate Future'),
                      ('eif','Equity Index Future'),
                      ('vif','Volatility Index Future'),
                      )

Collateral_Types = ((1,'UNDEFINED'),
                    (5,'BONDS'),
                    (8,'SR SECURED'),
                    (8,'SECURED'),
                    
                    (2,'UNSECURED'),
                    (3,'SR UNSECURED'),
                    (4,'BANK GUARANTEED'),
                    (5,'BONDS'),
                    (6,'UNSOBORDINATED'),
                    (7,'JR SUBORDINATED'),
                    (8,'SECURED'),
                    (9,''),
                    )

Coupon_type = django_choices(('FIXED','FLOATING','VARIABLE','ZERO_COUPON'),)

def TrimCode(code):
    code = str(code).upper()
    for c in ' .*':
        code = code.replace(c,'_')
    return code

def numeric_code(code):
    try:
        n = int(code)
        return str(n)
    except:
        return code