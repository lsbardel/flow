
from django.test import TestCase
from django.conf import settings

from jflow.db.trade.models import Trader,PortfolioDisplay
from jflow.db.finins import finins
from jflow.utils.anyjson import json



class FinInsTest(TestCase):
    fixtures = ['position.json','dataid.json','initial_data.json','exchange.json']
    
    def setUp(self):
        self.trader = Trader.objects.create_superuser('superuser', 'test@example.com', 'superpw', 'FI')
    
    def testPortfolio(self):
        name = 'LUCAFUND'
        portfolio = finins.get_portfolio(name = name)
        self.assertEqual(portfolio.name,name)
        pgen = portfolio.positions()
        positions = list(pgen)
        self.assertEqual(len(positions),3)
        for position in positions:
            security = position.security()
            ccy = position.ccy
            if security:
                self.assertEqual(ccy,security.ccy)
                self.assertEqual(security.id,position.sid)
                
    def testSerialization(self):
        name = 'LUCAFUND'
        portfolio = finins.get_portfolio(name = name)
        d = portfolio.todict()
        positions = d['positions']
        self.assertEqual(len(positions),3)
        js = portfolio.tojson()
        d2 = json.loads(js)
        positions = d2['positions']
        self.assertEqual(len(positions),3)
            
    def testPortfolioDisplay(self):
        d = PortfolioDisplay.objects.for_user(self.trader.user)
        self.assertEqual(d.count(),1)
        