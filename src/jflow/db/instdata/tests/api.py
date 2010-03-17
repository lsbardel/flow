import datetime

from django import http
from django.contrib.auth.models import User

from django.test import TestCase
from django.conf import settings
from django.utils import simplejson as json

import jflow


class MainTests(TestCase):
    fixtures = ['vendor.json',
                'datafield.json',
                'vendordatafield.json']
    
    def setUp(self):
        self.baseapi = '/api/instdata/'
        self.user = User.objects.create_user('jflowtest', 'jflowtest@world.com', 'jflowtest')
        self.user.is_active = True
        self.user.save()
        
    def tearDown(self):
        self.user.delete()


class ApiTest(MainTests):
        
    def testVersion(self):
        response = self.client.get('%sversion/' % self.baseapi)
        val = json.loads(response.content)
        self.assertEqual(val, jflow.get_version())
    
    