from django.conf import settings
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from jflow.db.instdata import models

ADMIN_URL_PREFIX = getattr(settings, 'ADMIN_URL_PREFIX', '/admin/') 

class FormTests(TestCase):
    fixtures = ['initial_data.json',
                'bondclass.json']
    
    def setUp(self):
        self.ct = models.CollateralType(name = 'collateral')
        self.ct.save()
        self.su = User.objects.create_superuser('superuser', 'test@example.com', 'superpw')
        self.client.login(username='superuser', password='superpw')
    
    def bond_data(self, code = 'A_BOND_CODE', country = 'GE', curncy = 'EUR'):
        ct = ContentType.objects.get_for_model(models.Bond)
        return {'code': code,
                'country': country,
                'bond_class': 1,
                'collateral_type': self.ct.pk,
                'content_type': ct.pk,
                'day_count': 'act360',
                'month_frequency': 12,
                'multiplier': 0.01,
                'settlement_delay': 3,
                'callable': False}
        
    def create_equity(self, code = 'abcd', country = 'US', curncy = 'EUR', instance = None):
        from jflow.db.instdata.forms import DataIdForm
        ct = ContentType.objects.get_for_model(models.Equity)
        f = DataIdForm({'code': code,
                        'country': country,
                        'content_type': '%s' % ct.id,
                        'curncy': curncy,
                        'multiplier': 1,
                        'settlement_delay': 2,
                        'live': True},
                        instance = instance)
        self.assertTrue(f.is_valid())
        return f.save()
    
    def create_bond(self, code = 'bond', country = 'GE', curncy = 'EUR', instance = None):
        from jflow.db.instdata.forms import DataIdForm
        f = DataIdForm(self.bond_data(code,country,curncy), instance = instance)
        self.assertTrue(f.is_valid())
        return f.save()
    
    def get(self, code):
        return models.DataId.objects.get(code = code)
    
    def testNoInstrument1(self):
        from jflow.db.instdata.forms import DataIdForm
        f = DataIdForm({'code': 'spxt','country':'US'})
        self.assertTrue(f.is_valid())
        id = f.save()
        self.assertEqual(id.code,'SPXT')
    
    def testAddEquity(self):
        id = self.create_equity()
        self.assertEqual(id.code,'ABCD')
        self.assertEqual(id.curncy,'EUR')
        self.assertTrue(id.live)
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
        
    def testAdmin(self):
        if 'django.contrib.admin' in settings.INSTALLED_APPS:
            data = self.bond_data(code = 'dbr54')
            data['vendorid_set-TOTAL_FORMS'] = 3
            data['vendorid_set-INITIAL_FORMS'] = 0
            data['vendorid_set-MAX_NUM_FORMS'] = 0
            response = self.client.post('%sinstdata/dataid/add/' % ADMIN_URL_PREFIX, data)
            self.assertEqual(response.status_code,302)
            id = self.get('DBR54')
            self.assertEqual(id.type,'bond')
        
        