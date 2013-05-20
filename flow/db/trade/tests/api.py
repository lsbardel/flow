import base64

from django.test import TestCase
from django.conf import settings
from django.utils import simplejson as json

from jflow.db.trade import models

class ApiTest(TestCase):
    fixtures = ['funds.json']
    fundcode = 'BONDUK'
    team = 'FI'
    
    def setUp(self):
        self.baseapi = '/api/trade/'
        self.trader = models.Trader.objects.create_superuser('superuser', 'test@example.com', 'superpw', 'FI')
        self.auth_string = 'Basic %s' % base64.encodestring('superuser:superpw').rstrip()
    
    def testGetAllFunds(self):
        '''
        Get all funds from database
        '''
        response = self.client.get('%sfund/' % self.baseapi, HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        self.assertEqual(len(res),models.Fund.objects.all().count())
        
    def testGetOneFunds(self):
        response = self.client.get('%sfund/%s/' % (self.baseapi,self.fundcode), HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        self.assertEqual(res['code'],self.fundcode)
        
    def testTeamFunds(self):
        response = self.client.get('%sfundteam/%s/' % (self.baseapi,self.team), HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        for f in res:
            team = f['fund_holder']
            self.assertEqual(team['code'],self.team)
        
    
