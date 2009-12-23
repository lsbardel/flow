'''
Remove badly formed positions from database
'''
import os
import re
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
 
from jflow.db.instdata.models import InstrumentCode
 

 
class Command(BaseCommand):
    help = "Clean prospero instruments"
 
    def handle(self, *args, **options):
        # Determine the project_name a bit naively -- by looking at the name of
        # the parent directory.        
        tr = 0
        for ic in InstrumentCode.objects.all():
            inst = ic.instrument()
            if not inst:
                tr += 1
                ic.delete()
                
        if tr:
            print('Removed %s Instrument Codes' % tr)
        else:
            print('Instruments were OK')

