from datetime import date,timedelta
from itertools import izip
from timeit import default_timer as timer
import logging

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger('Portfolio Tests')

from random import randint, uniform
from django.conf import settings

from stdnet import orm
from stdnet.utils import populate

import ccy
from jflow.db.trade.models import Fund
from jflow.models import *
from jflow.utils.anyjson import json
from jflow.utils.tests import jFlowTest
from jflow import api


class TestDatabaseCacheInteraction(jFlowTest):
    fixtures = ['random_data.json']
    
    def randomFund(self):
        funds = Fund.objects.all()
        N = funds.count()
        return funds[randint(1,N-1)]
    
    def testLoadPortfolio(self):
        '''Load default portfolio view from Fund django object'''
        fund = self.randomFund()
        view = api.get_portfolio_object(fund)
        portfolio = view.portfolio
        self.assertEqual(portfolio.name,fund.code)
        self.assertEqual(view.ccy,fund.curncy)
        view2 = api.get_portfolio_object(fund)
        self.assertEqual(view,view2)
        self.assertEqual(view.portfolio,view2.portfolio)
        folders = view.folders.all()
        self.assertTrue(folders.count()>0)