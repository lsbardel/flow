import datetime
import csv
import base64
import os

from django import http
from django.contrib.auth.models import User

from django.test import TestCase
from django.conf import settings
from django.utils import simplejson as json

import jflow


class MainTests(TestCase):
    fixtures = ['initial_data.json',
                'bondclass.json']
    
    def setUp(self):
        self.baseapi = '/api/instdata/'
        self.su = User.objects.create_superuser('superuser', 'test@example.com', 'superpw')
        self.auth_string = 'Basic %s' % base64.encodestring('superuser:superpw').rstrip()
        
    def tearDown(self):
        self.su.delete()


class ApiTest(MainTests):
    
    def testVersion(self):
        response = self.client.get('%sversion/' % self.baseapi)
        val = json.loads(response.content)
        self.assertEqual(val, jflow.get_version())
        
    def loadids(self):
        name = os.path.join(os.path.dirname(__file__),'dataid.csv')
        f = open(name,'r')
        rows =  csv.DictReader(f)
        data = []
        res  = []
        for row in rows:
            d = {}
            for key,val in row.items():
                if key == 'result':
                    res.append(val)
                else:
                    if val == 'TRUE':
                        val = True
                    elif val == 'FALSE':
                        val = False
                    elif isinstance(val,str):
                        try:
                            val = val.encode('utf-8')
                        except:
                            val = ''
                    d[key] = val
            data.append(d)
        return data,res

    def testCreateInstruments(self):
        '''
        Full Bond creation with bondclass and issuer
        '''
        data,res = self.loadids()
        data = {'data': json.dumps(data)}
        response = self.client.post('%sdata/' % self.baseapi, data, HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        
        