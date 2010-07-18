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
from jflow.db.trade.models import Fund, FundHolder, Trader
from jflow.models import *
from jflow.utils.anyjson import json
from jflow.utils.tests import jFlowTest
from jflow import api


class TestDatabaseCacheInteraction(jFlowTest):
    loadonce = True
    fixtures = ['random_data.json']
    
    def initialize(self):
        Trader.objects.create_superuser('pippo', 'test@example.com', 'superpw', self.randomGroup())
    
    def randomGroup(self):
        groups = FundHolder.objects.all()
        N = groups.count()
        return groups[randint(1,N-1)]
    
    def randomFund(self):
        funds = Fund.objects.all()
        N = funds.count()
        return funds[randint(1,N-1)]
    
    def testLoadDefaultPortfolioView(self):
        '''Load default portfolio view from a Fund Django object'''
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
        t = 0
        for folder in folders:
            positions = folder.positions
            t += positions.size()
        N = fund.position_set.filter(dt = view.dt).count()
        self.assertEqual(t,N)
        self.assertEqual(view.user,None)
        
    def testUserView(self):
        fund = self.randomFund()
        view = api.get_portfolio_object(fund, user = 'pippo')
        portfolio = view.portfolio
        self.assertEqual(view.user,None)
        view2 = api.create_user_view(fund, 'pippo-view', 'pippo')
        view3 = api.create_user_view(fund, 'pippo-view2', 'pippo')
        self.assertEqual(view2.user,'pippo')
        self.assertEqual(view3.user,'pippo')
        self.assertEqual(view2.portfolio,portfolio)
        self.assertEqual(view3.portfolio,portfolio)
        self.assertEqual(view2.name,'pippo-view')
        self.assertEqual(view3.name,'pippo-view2')
        self.assertTrue(view2.isdefault('pippo'))
        self.assertFalse(view3.isdefault('pippo'))
        self.assertTrue(view2.id > view.id)
        self.assertTrue(view3.id > view2.id)
        view4 = api.create_user_view(fund, 'pippo-view2', 'pippo', default = True)
        self.assertEqual(view4,view3)
        self.assertFalse(view2.isdefault('pippo'))
        self.assertTrue(view3.isdefault('pippo'))
        
    
    