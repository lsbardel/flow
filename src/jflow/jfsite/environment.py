import os
from utils.pathtool import AddToPath, parentdir

local_dir = parentdir(os.path.abspath(__file__))

pt = AddToPath(local_dir)

pt.add(module='djpcms',uplev = 3, down = ('djpcms',))
pt.add(module = 'ccy', uplev = 3, down = ('ccy',))


def setup(setting_module):
    s2 = 'jflow.jfsite.allsettings.%s' % setting_module 
    os.environ['JFLOW_SETTINGS_MODULE']   = s2
    os.environ['STDNET_SETTINGS_MODULE']  = s2
    os.environ['UNUK_SETTINGS_MODULE']    = s2
    os.environ['DJANGO_SETTINGS_MODULE']  = s2
    

