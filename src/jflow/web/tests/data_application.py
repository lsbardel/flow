from django.test import TestCase
from django.contrib.auth.models import User

from djpcms.views import appsite
from djpcms.views.apps.user import UserApplication
from djpcms.utils.uniforms import UniForm

from jflow.web.applications import data
from jflow.web.forms import num_vendor_inlines

data0 = {
        'vendors-TOTAL_FORMS': num_vendor_inlines,
        'vendors-INITIAL_FORMS': 0,
        'vendors-MAX_NUM_FORMS': 0,
        }


class TestDataApplication(TestCase):
    fixtures = ['initial_data.json','bondclass.json']
    
    def setUp(self):
        appsite.site.register('/accounts/', UserApplication, model = User)
        appsite.site.register('/data/', data.DataApplication, model = data.DataId)
        User.objects.create_superuser('luca', 'luca@sbardy.com', 'sbardy')
        result = self.client.login(username='luca', password='sbardy')
        self.failUnlessEqual(result, True)
    
    def testEquity(self):
        from jflow.db.instdata.utils import instrument_ct
        dd = {'code':'GOOG',
                'content_type':instrument_ct('equity').id,
                'curncy':'USD'}
        dd.update(data0)
        c = self.client
        response = c.get('/data/add/')
        self.assertEqual(response.status_code,200)
        response = c.post('/data/add/', dd)
        self.assertEqual(response.status_code,200)
        html = response.content
        self.assertTrue('id_CUSIP' in html)
        self.assertTrue('id_SEDOL' in html)
        self.assertTrue('id_exchange' in html)
        self.assertTrue('id_security_type' in html)
        self.assertTrue('id_multiplier' in html)
        self.assertTrue('id_settlement_delay' in html)
        
    def testBond(self):
        from jflow.db.instdata.utils import instrument_ct
        dd = {'code':'DBR20',
              'content_type':instrument_ct('bond').id,
              'coupon': 5.675}
        dd.update(data0)
        c = self.client
        response = c.get('/data/add/')
        self.assertEqual(response.status_code,200)
        response = c.post('/data/add/', dd)
        self.assertEqual(response.status_code,200)
        html = response.content
        self.assertTrue('id_CUSIP' in html)
        self.assertTrue('id_SEDOL' in html)
        self.assertTrue('id_exchange' in html)
        self.assertTrue('id_bond_class' in html)
        self.assertTrue('id_coupon' in html)
        self.assertTrue('5.675' in html)
        self.assertTrue('id_announce_date' in html)
        
    def tearDown(self):
        self.client.logout()
        appsite.site.unregister(User)
        appsite.site.unregister(data.DataId)