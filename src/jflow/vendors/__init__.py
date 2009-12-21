
import base
import google
import blb
import ecb
import jflowdata

def get_vendor(code):
    code = '%s' % code.lower()
    return base.vendors.get(code,None)