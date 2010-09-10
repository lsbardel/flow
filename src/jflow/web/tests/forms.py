from django.test import TestCase
from jflow.db.instdata import instrument_type
from djpcms.utils.uniforms import UniForm

class TestDataIdForm(TestCase):
    fixtures = ['initial_data.json','bondclass.json']
    
    def testEquity(self):
        from jflow.web.forms import NiceDataIdForm
        data = {'code':'GOOG',
                'content_type':instrument_type('equity').id,
                'curncy':'USD'}
        self.assertFalse(NiceDataIdForm(data = data).is_valid())
        data.update({'country':'US'})
        self.assertFalse(NiceDataIdForm(data = data).is_valid())
        data.update({'multiplier':1})
        self.assertFalse(NiceDataIdForm(data = data).is_valid())
        data.update({'settlement_delay':2})
        form = NiceDataIdForm(data = data)
        self.assertFalse(form.is_valid())
        html = UniForm(form).render()
        self.assertTrue('id_CUSIP' in html)
        self.assertTrue('id_SEDOL' in html)
        self.assertTrue('id_security_type' in html)