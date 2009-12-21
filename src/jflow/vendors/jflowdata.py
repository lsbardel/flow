
from jflow.db.instdata.models import MktData, DataField

from base import *

class manual(DataVendor):
    
    def cache_factory(self):
        return MktData.objects
    
    def external(self):
        return False

manual()
            