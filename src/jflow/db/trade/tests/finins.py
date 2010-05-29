
from django.test import TestCase
from django.conf import settings
from jflow.db.finins import FinRoot


root = FinRoot()

class FinInsTest(TestCase):
    fixtures = ['position.json','dataid.json','initial_data.json','exchange.json']
    
    def setUp(self):
        pass
    
    def testPortfolio(self):
        name = 'LUCAFUND'
        portfolio = root.get_portfolio(name = name)
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
            
        