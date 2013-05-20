'''Add currencies to the database'''
import os
import logging
import optparse
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module

from ccy import currencydb
from jflow.db.instdata.models import DataId
 

 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-d", "--defaultvendor", 
            dest="defaultvendor", 
            action="append", 
            help="Default Vendor"
        ),
    )
    help = "Add currencies to database"
 
    def handle(self, *args, **options):
        from jflow.conf import settings
        level = {
            '0': logging.WARN, 
            '1': logging.INFO, 
            '2': logging.DEBUG
        }[options.get('verbosity', '1')]
        logging.basicConfig(level=level, format="%(name)s: %(levelname)s: %(message)s")
        logger = logging.getLogger('addccy')
        
        dv = options.get('defaultvendor', None)
        if dv:
            dv = unicode(dv[0])        
        ccys = currencydb()
        for c in ccys.values():
            id,created = DataId.objects.get_or_create(code = c.code,
                                                      country = c.default_country,
                                                      default_vendor = dv,
                                                      name = '%s Spot Rate' % c.as_cross('/'),
                                                      tags = 'forex currency spot index')
            id.add_vendor('blb','%s Curncy' % c.code)
            id.add_vendor('ecb',c.code)
            
            if created:
                logger.info("Created currency %s" % id)
            else:
                logger.info("Modified currency %s" % id)
            