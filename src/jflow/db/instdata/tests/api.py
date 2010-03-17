import datetime

from django.test import TestCase
from django.conf import settings


class CalendarViewTest(TestCase):
    fixtures = ["vendor.json"]
        
    def testVersion(self):
        pass