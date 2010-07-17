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

# Number of instruments
NUMINSTS = 100
GROUPS   = 3
NUMFUNDS = 5
NUMDATES = 2
MIN_POSITIONS_PER_FUND = 10
MAX_POSITIONS_PER_FUND = 30


#Create Random Data
ccys       = ccy.all()
instnames  = populate('string',NUMINSTS,min_len = 3, max_len = 10)
insttypes  = populate('choice',NUMINSTS,choice_from=['equity','bond','future'])
instccys   = populate('choice',NUMINSTS,choice_from=ccys)

groupnames = populate('string',GROUPS,min_len = 2, max_len = 5)

fundnames  = populate('string',NUMFUNDS,min_len=5,max_len=10)
fundccys   = populate('choice',NUMFUNDS,choice_from=['EUR','GBP','USD'])
fundgroups = populate('choice',NUMFUNDS,choice_from=groupnames)
dates      = populate('date',NUMDATES,start=date.today()-timedelta(3*360))


class FinInsTest(jFlowTest):
    
    def setUp(self):
        self.user  = 'superman'
        
    def fill(self):
        t = timer()
        for name,ccy,typ in izip(instnames,instccys,insttypes):
            FinIns(name = name, ccy = ccy, type = typ).save()
        logger.info('Built %s instruments in %s seconds' % (NUMINSTS,timer()-t))
        n = 0
        t = timer()
        for name,ccy,group in izip(fundnames,fundccys,fundgroups):
            holder = PortfolioHolder(name = name, ccy = ccy, group = group).save()
            for dt in dates:
                n+=1
                Portfolio(holder = holder, dt = dt).save()
        logger.info('Built %s master portfolios in %s seconds' % (n,timer()-t))
        funds  = Portfolio.objects.all()
        finins = list(FinIns.objects.all())
        n      = 0
        t      = timer()
        for fund in funds:
            npos = randint(MIN_POSITIONS_PER_FUND,MAX_POSITIONS_PER_FUND)
            for inst in populate('choice',npos,choice_from = finins):
                pos = Position.objects.filter(portfolio = fund, instrument = inst)
                if not pos:
                    n += 1
                    fund.addnewposition(inst, size = randint(10,10000), value = uniform(20000,100000))
        logger.info('Built %s positions in %s seconds' % (n,timer()-t))
    
    def testDefaultView(self):
        '''Test the default view'''
        self.fill()
        funds = PortfolioHolder.objects.filter(parent = None)
        # pick a random fund
        holder = funds[randint(0,len(funds)-1)]
        funds  = holder.dates.all()
        fund   = funds[randint(0,len(funds)-1)]
        # call the api to obtain the view
        view = api.get_portfolio_object(fund)
        self.assertEqual(view.portfolio,fund)
        self.assertEqual(view.name,'default')
        self.assertEqual(view.ccy,fund.ccy)
        folders = view.folders.all()
        self.assertTrue(folders.count()>0)
        #The total number of positions in folders
        #must be the same as the number of position in porfolio
        N = 0
        for folder in folders:
            N += folder.positions.size()
        self.assertEqual(N,fund.positions.all().count())
        
    def _get_id(self, name, dt = None):
        fund = Fund.objects.get(code = name)
        instance = api.get_portfolio_object(fund)
        return api.get_object_id(instance,dt)
    
    def _testDefaultPortfolioView(self):
        '''Test the default view of a portfolio. No user specified.'''
        id = self.get_id('LUCAFUND',self.dt)
        p  = api.get(id)
        self.assertEqual(p.dt,self.dt)
        self.assertTrue(p.folder)
        
    def _testAddPortfolioView(self):
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
            
    def _testPortfolioDisplay(self):
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
        