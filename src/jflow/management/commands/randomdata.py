import logging
import optparse
import os
from datetime import date, timedelta
from itertools import izip
from random import randint
 
from django.contrib.contenttypes.management import update_all_contenttypes
from django.core.management.base import copy_helper, CommandError, BaseCommand
from django.utils.importlib import import_module
from django.utils.dateformat import format

import ccy
from jflow import api
from stdnet.utils import populate
from jflow.db.instdata.models import DataId
from jflow.db.trade.models import FundHolder, Fund, Position
 
#5D-tuple of NUM_INSTS, NUM_GROUPS, NUM_FUNDS, AVERAGE NUM_POSITION/FUND, NUM_DATES
SIZES = {1: (10,   1, 2,   4,  1),        # tiny
         2: (50,   2, 5,   10, 3),        # small
         3: (100,  3, 10,  20, 10),       # medium
         4: (300,  4, 30,  30, 30),       # large
         5: (2000, 6, 100, 40, 100)}      # huge

 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            "-s", "--size", 
            dest   = "size",
            action = "store_const",
            help   = "Size of data, in range 1 (tiny) to 5 (huge)",
            default = 3,
        ),
    )
    help = "Fill database with random data for testing purposes"
 
    def handle(self, *args, **options):
        from django.conf import settings
        level = {
            '0': logging.WARN, 
            '1': logging.INFO, 
            '2': logging.DEBUG
        }[options.get('verbosity', '1')]
        logging.basicConfig(level=level, format="%(name)s: %(levelname)s: %(message)s")
        logger = logging.getLogger('randomdata')
        size   = SIZES.get(int(options.get('size')),None)
        DataId.objects.all().delete()
        FundHolder.objects.all().delete()
        
        NUM_INSTS, NUM_GROUPS, NUM_FUNDS, NUM_POS, NUM_DT = size
        inst_types = ['equity']
        #inst_types = api.instrument_types()
        dataids = populate('string', NUM_INSTS,  min_len = 3, max_len = 20)
        groups  = populate('string', NUM_GROUPS, min_len = 2, max_len = 5)
        ccys    = populate('choice', NUM_INSTS,  choice_from = ccy.g10m())
        fnames  = populate('string', NUM_FUNDS,  min_len = 5, max_len = 10)
        fcys    = populate('choice', NUM_FUNDS,  choice_from = ccy.g7())
        types   = populate('choice', NUM_INSTS,  choice_from = inst_types)
        dates   = populate('date', NUM_DT, start = date.today()-timedelta(1000), end = date.today())
        logger.info('Building %s random Data Ids' % NUM_INSTS)
        codes = set()
        for code,c,typ in izip(dataids,ccys,types):
            if code in codes:
                continue
            codes.add(code)
            id = api.adddataid(code, c, type = typ, tags='randomdata')
        logger.info('Building %s random Groups' % NUM_GROUPS)
        for name in groups:
            FundHolder(code = name, fund_manager = True).save()
        groups = list(FundHolder.objects.all())
        NUM_GROUPS = len(groups)
        i = 0
        codes = set()
        instruments = list(DataId.objects.all())
        NUM_INSTS = len(instruments)
        for code,c in izip(fnames,fcys):
            i += 1
            if code in codes:
                continue
            codes.add(code)
            logger.info('Building random Fund %s of %s' % (i,NUM_FUNDS))
            g = groups[randint(0,NUM_GROUPS-1)]
            fund = Fund(code = code, firm_code = code, curncy = c, fund_holder = g)
            fund.save()
            ddates = set()
            for dt in dates:
                if dt in ddates:
                    continue
                ddates.add(dt)
                npos = randint(int(0.5*NUM_POS), int(1.5*NUM_POS))
                logger.info('Building %s random Positions for Fund %s of %s @ %s' % (npos,i,NUM_FUNDS,dt))
                values = populate('float', npos,  start = 200.0, end = 100000.0)
                sizes  = populate('integer', npos,  start = 10, end = 1000)
                insts = set()
                for size,value in izip(sizes,values):
                    inst = instruments[randint(0,NUM_INSTS-1)]
                    while inst in insts:
                        inst = instruments[randint(0,NUM_INSTS-1)]
                    insts.add(inst)
                    Position(fund = fund, dataid = inst, size = size, value = value, dt = dt).save()
                    
                    
                
                
                
        
        
        
        