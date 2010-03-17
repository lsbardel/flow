import datetime

from django import http
from django.contrib.auth.models import User

from django.test import TestCase
from django.conf import settings


class MainTests(TestCase):
    fixtures = ['vendor.json',
                'datafield.json',
                'vendordatafield.json']
    
    def setUp(self):
        self.user = User.objects.create_user('jflowtest', 'jflowtest@world.com', 'jflowtest')
        self.user.is_active = True
        self.user.save()
        
    def tearDown(self):
        self.user.delete()


class ApiTest(MainTests):
        
    def testVersion(self):
        response = self.client.get('/api/instdata/version/')
        self.assertTrue(isinstance(response,http.HttpResponse))