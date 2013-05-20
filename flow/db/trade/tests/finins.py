import datetime

from django.test import TestCase
from django.conf import settings

from jflow.db.trade.models import Trader,PortfolioDisplay,Fund
from jflow.utils.anyjson import json
from jflow import api



class FinInsTest(TestCase):
    fixtures = ['position.json','dataid.json','initial_data.json','exchange.json']
    
    def setUp(self):
        self.dt = datetime.date(2010,6,1)
        trader = Trader.objects.create_superuser('superuser', 'test@example.com', 'superpw', 'FI')
        self.user = trader.user
    
    def get_id(self, name, dt = None):
        fund = Fund.objects.get(code = name)
        instance = api.get_portfolio_object(fund)
        return api.get_object_id(instance,dt)
    
    def testDefaultPortfolioView(self):
        '''Test the default view of a portfolio. No user specified.'''
        id = self.get_id('LUCAFUND',self.dt)
        p  = api.get(id)
        self.assertEqual(p.dt,self.dt)
        self.assertTrue(p.folder)
        
    def testAddPortfolioView(self):
        id = self.get_id('LUCAFUND',self.dt)
        try:
            api.add_new_portfolio_view(id,None,'test-view')
            self.fail("A value Error should have occurred")
        except ValueError:
            pass
        except:
            self.fail("A value Error should have occurred")
        v = api.add_new_portfolio_view(id,self.user.username,'test-view')
        
        
        
        
    def _testwhat(self):
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
                
    def _testSerialization(self):
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
        d = PortfolioDisplay.objects.for_user(self.user)
        self.assertEqual(d.count(),1)
        
    def _testLoadFundFromId(self):
        '''Load Fund from id'''
        name = 'LUCAFUND'
        obj = Fund.objects.get(code = name)
        id = finins.get_object_id(obj, datetime.date(2010,6,1))
        fi = finins.get(id)
        self.assertEqual(fi.id,id)
        jd = fi.tojson()
        