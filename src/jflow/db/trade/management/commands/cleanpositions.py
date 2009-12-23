'''
Remove badly formed positions from database
'''
import os
import re
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
 
from jflow.db.trade.models import Position
 
_special_tags = {}
 
class Command(BaseCommand):
    help = "Clean prospero positions"
 
    def handle(self, *args, **options):
        # Determine the project_name a bit naively -- by looking at the name of
        # the parent directory.        
        tr = 0
        for pos in Position.objects.all():
            if not pos.positionhistory_set.all():
                tr += 1
                pos.delete()
                
        if tr:
            print('Removed %s Positions' % tr)
        else:
            print('Positions were OK')