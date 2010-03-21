from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from jflow.db.instdata.forms import DataIdForm
from jflow.db.instdata import models


class FormTests(TestCase):
    fixtures = ['initial_data.json',
                'bondclass.json']
    
    def setUp(self):
        self.ct = models.CollateralType(name = 'collateral')
        self.ct.save()
        
    def create_equity(self, code = 'abcd', country = 'US', curncy = 'EUR', instance = None):
        ct = ContentType.objects.get_for_model(models.Equity)
        f = DataIdForm({'code': code,
                        'country': country,
                        'content_type': '%s' % ct.id,
                        'curncy': curncy,
                        'multiplier': 1,
                        'settlement_delay': 2},
                        instance = instance)
        self.assertTrue(f.is_valid())
        return f.save()
    
    def create_bond(self, code = 'bond', country = 'GE', curncy = 'EUR', instance = None):
        ct = ContentType.objects.get_for_model(models.Bond)
        f = DataIdForm({'code': code,
                        'country': country,
                        'bond_class': 1,
                        'collateral_type': self.ct.pk,
                        'content_type': ct.pk,
                        'day_count': 'act360',
                        'month_frequency': 12,
                        'multiplier': 0.01,
                        'settlement_delay': 3,
                        'callable': False},
                        instance = instance)
        self.assertTrue(f.is_valid())
        return f.save()
    
    def testNoInstrument1(self):
        f = DataIdForm({'code': 'spxt','country':'US'})
        self.assertTrue(f.is_valid())
        id = f.save()
        self.assertEqual(id.code,'SPXT')
    
    def testAddEquity(self):
        id = self.create_equity()
        self.assertEqual(id.code,'ABCD')
        self.assertEqual(id.curncy,'EUR')
        self.assertEqual(id.instrument.code,id.code)
        self.assertEqual(id.instrument.ccy(),id.curncy)
        self.assertEqual(id.type,'equity')
        id = models.DataId.objects.get(code = 'ABCD')
        self.assertEqual(id.instrument.code,id.code)
        self.assertEqual(id.instrument.ccy(),id.curncy)
        self.assertEqual(id.type,'equity')
        
    def testModifyEquity(self):
        '''
        Modify an equity object
        '''
        id = self.create_equity(code='vod_ln', curncy = 'EUR')
        self.assertEqual(id.code,'VOD_LN')
        id = models.DataId.objects.get(code = 'VOD_LN')
        inst = id.instrument
        nid = self.create_equity(code = 'vod_lon', country = 'UK', curncy = 'USD', instance = id)
        self.assertEqual(id.pk,nid.pk)
        self.assertEqual(nid.code,'VOD_LON')
        self.assertEqual(inst.pk,nid.instrument.pk)
        self.assertEqual(nid.curncy,'USD')
        self.assertEqual(nid.instrument.code,nid.code)
        self.assertEqual(nid.instrument.ccy(),nid.curncy)
        self.assertEqual(nid.type,'equity')
        
    def testAddBond(self):
        id = self.create_bond(code='dbrbond')
        self.assertEqual(id.type,'bond')
        self.assertEqual(id.instrument.bond_class.code,'DBR')
        
    def testModifyEquityBond(self):
        id = self.create_equity(code='vod_ln', curncy = 'EUR')
        id = models.DataId.objects.get(code = 'VOD_LN')
        nid = self.create_bond(code = 'VODBOND', instance = id)
        self.assertEqual(nid.type,'bond')
        eqs = models.Equity.objects.filter(code = 'VOD_LN')
        self.assertEqual(eqs.count(),0)
        
        self.assertEqual(id.type,'bond')
        self.assertEqual(id.instrument.bond_class.code,'DBR')
        
        