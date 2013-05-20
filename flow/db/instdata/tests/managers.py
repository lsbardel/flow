

from django.test import TestCase

from jflow.db.instdata.models import DataId

__all__ = ['DataIdManagerTest',
           ]

class DataIdManagerTest(TestCase):
    
    def testCreateDataIdwithNoType(self):
        code = u'MSCI_W'
        name = 'MSCI WORLD FREE USD'
        description = 'World Index'
        country = 'US'

        did ,created = DataId.objects.get_or_create(code = code , name = name , description = description , country = country)
        self.assertTrue(did)
        inst = did.instrument
        self.assertTrue(inst is None)
        
        
        
    