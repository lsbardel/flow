from datetime import date,timedelta
from itertools import izip
from timeit import default_timer as timer
import logging

logging.basicConfig(level = logging.DEBUG)
logger = logging.getLogger('Portfolio Tests')

from random import randint, uniform
from django.conf import settings

from stdnet import orm
from stdnet.utils import populate

import ccy
from jflow.models import *
from jflow.utils.anyjson import json
from jflow.utils.tests import jFlowTest
from jflow import api


class TestDatabaseCacheInteraction(jFlowTest):
    
    def testLoadPortfolio(self):
        pass