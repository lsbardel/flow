'''
Rollback positions and positions history to a specified date
'''
import logging
import optparse
import os
import datetime
import dateutil.parser
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
from django.utils.dateformat import format
 
from jflow.db.trade.models import Position, PositionHistory
 
_special_tags = {}
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-d", "--date", 
            dest="date", 
            action="append", 
            help="Date to roll back the position to. Format yyyy"
        ),
    )
    help = "Clean prospero positions"
 
    def handle(self, *args, **options):
        from django.conf import settings
        level = {
            '0': logging.WARN, 
            '1': logging.INFO, 
            '2': logging.DEBUG
        }[options.get('verbosity', '0')]
        logging.basicConfig(level=level, format="%(name)s: %(levelname)s: %(message)s")
        logger = logging.getLogger('rollback')
        dt = options.get('date', None)
        if dt:
            try:
                dt = dt[0]
                dt = dateutil.parser.parse(dt).date()
            except:
                logger.error("date %s not in correct format" % dt)
                return
        else:
            dt = datetime.date.today()
            
        response = raw_input('Confirm rollback to %s (y/n): ' % format(dt,settings.DATE_FORMAT))
        
        if response.lower() == 'y':
            pos  = Position.objects.filter(open_date__gte = dt)
            RP   = pos.count()
            if not RP:
                logger.info("No positions. quitting, nothing done")
                return
        
            logger.info("Removing %s positions" % RP)
            pos.delete()
            hist = PositionHistory.objects.filter(dt__gte = dt)
            logger.info("Removing %s position histories" % hist.count())
            hist.delete()
        
        