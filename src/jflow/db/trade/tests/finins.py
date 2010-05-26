
from django.test import TestCase
from django.conf import settings
from jflow.db.finins import FinRoot


root = FinRoot()

class FinInsTest(TestCase):
    fixtures = ['position.json','dataid.json','initial_data.json','exchange.json']
    
    def testPortfolio(self):
        name = 'LUCAFUND'
        portfolio = root.get_portfolio(name = name)
        self.assertEqual(portfolio.name,name)
        pos = portfolio.positions()
        positions = [p for p in pos]
        self.assertEqual(len(positions),2)