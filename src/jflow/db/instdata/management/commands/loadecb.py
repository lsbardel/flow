'''Load ecb currency data to database'''
import os
import logging
import optparse
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module

from ccy import currencydb
from ccy.data.ecb import ecbzipccy
from jflow.db.instdata.models import DataId, MktData, DataField
 

class write_to_db(object):
    '''Hook to write ecb data into jflow database'''
    def __init__(self, field):
        self._vendors = {}
        self.field = field 
        
    def getvendor(self, code):
        v = self._vendors.get(code,None)
        if not v:
            d = DataId.objects.get(code =code)
            v = d.vendors.get(vendor__code = 'ECB')
            self._vendors[code] = v
        return v
            
    def __call__(self, ccy, dt, val):
        '''Write to database'''
        v = self.getvendor(ccy)
        obj,created = MktData.objects.get_or_create(vendor_id = v,
                                                    dt = dt,
                                                    mkt_value = val,
                                                    field = self.field)

 
class Command(BaseCommand):
    help = "Add currencies data to database from ECB web site"
 
    def handle(self, *args, **options):
        from jflow.conf import settings
        field = DataField.objects.get(code = settings.DEFAULT_DATA_FIELD)
        handler = write_to_db(field) 
        ecbzipccy(handler = handler)
        