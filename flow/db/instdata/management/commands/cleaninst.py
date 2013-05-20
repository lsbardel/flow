'''
Remove badly formed positions from database
'''
import os
import re
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
 
from jflow.db.instdata.models import DataId
from jflow.db.trade.models import Position
 

 
class Command(BaseCommand):
    help = "Clean prospero instruments"
 
    def handle(self, *args, **options):     
        tr = 0
        ids = DataId.objects.exclude(isin = '')
        isin = {}
        for id in ids:
            nid = isin.get(id.isin,None)
            if not nid:
                isin[id.isin] = id
            else:
                fc = id.firm_code or nid.firm_code
                did = nid
                if nid.instrument:
                    did = id
                    id = nid
                id.firm_code = fc
                id.save()
                pos = Position.objects.filter(dataid = did)
                for p in pos:
                    pc = Position.objects.filter(dataid = id, dt = p.dt, fund = p.fund)
                    if not pc:
                        p.dataid = id
                        p.save()
                did.delete()
                tr += 1
                                
        if tr:
            print('Removed %s dataids' % tr)
        else:
            print('Data ids were OK')

