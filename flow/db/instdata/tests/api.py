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


def loadtestids(name):
    name = os.path.join(os.path.dirname(__file__),name)
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


class MainTests(TestCase):
    fixtures = ['initial_data.json',
                'bondclass.json',
                'futurecontract.json',
                'exchange.json',]
    
    def setUp(self):
        self.baseapi = '/api/instdata/'
        self.su = User.objects.create_superuser('superuser', 'test@example.com', 'superpw')
        self.auth_string = 'Basic %s' % base64.encodestring('superuser:superpw').rstrip()
        
    def tearDown(self):
        self.su.delete()


class ApiTest(MainTests):
    VendorTest = 'blb'
    typetest = 'equity'
    
    def testVersion(self):
        response = self.client.get('%sversion/' % self.baseapi)
        val = json.loads(response.content)
        self.assertEqual(val, jflow.get_version())

    def testCreateInstruments(self):
        '''
        Full Bond creation with bondclass and issuer
        '''
        input_data, expres = loadtestids('dataid.csv')
        data = {'data': json.dumps(input_data)}
        response = self.client.post('%sdata/' % self.baseapi, data, 
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        self.assertTrue(res["committed"])
        result = res.get("result",[])
        self.assertEqual(len(result),len(input_data))
        for r,re in zip(result,expres):
            self.assertEqual(r['result'],re)
            
    def testCreateDataIdWithBadIssuer(self):
        input_data, expres = loadtestids('dataid_with_no_issuer.csv')
        data = {'data': json.dumps(input_data)}
        response = self.client.post('%sdata/' % self.baseapi, data, 
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        self.assertTrue(res["committed"])
        result = res.get("result",[])
        self.assertEqual(len(result),len(input_data))
        for r,re in zip(result,expres):
            self.assertEqual(r['result'],re)

    def testCreateDataIdWithBadDayCount(self):
        input_data, expres = loadtestids('dataid_with_bad_day_count.csv')
        data = {'data': json.dumps(input_data)}
        response = self.client.post('%sdata/' % self.baseapi, data, 
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        self.assertTrue(res["committed"])
        result = res.get("result",[])
        self.assertEqual(len(result),len(input_data))
        for r,re in zip(result,expres):
            self.assertEqual(r['result'],re)
     
        
    
    def testVendorIdFromVendorAllTypes(self):
        vtest = self.VendorTest.upper()
        response = self.client.get('%svendorid/%s/' % (self.baseapi,self.VendorTest),
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        for r in res:
            self.assertEqual(r['vendor'],vtest)
    
    def testVendorIdFromVendorNullTypes(self):
        vtest = self.VendorTest.upper()
        response = self.client.get('%svendorid/%s/none/' % (self.baseapi,self.VendorTest),
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        for r in res:
            id = r['dataid']
            self.assertEqual(r['vendor'],vtest)
            self.assertEqual(id['content_type'],None)
    
    def testVendorIdFromVendorWithType(self):
        vtest = self.VendorTest.upper()
        response = self.client.get('%svendorid/%s/%s/' % (self.baseapi,self.VendorTest,self.typetest),
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        for r in res:
            id = r['dataid']
            self.assertEqual(r['vendor'],vtest)
            self.assertEqual(id['content_type'],self.typetest)
    
    def testCreateFuture(self):
        input_data, expres = loadtestids('future.csv')
        data = {'data': json.dumps(input_data)}
        response = self.client.post('%sdata/' % self.baseapi, data, 
                                    HTTP_AUTHORIZATION=self.auth_string)
        self.assertEqual(response.status_code,200)
        res = json.loads(response.content)
        self.assertTrue(res["committed"])
        result = res.get("result",[])
        self.assertEqual(len(result),len(input_data))
        for r,re in zip(result,expres):
            self.assertEqual(r['result'],re)
        
        