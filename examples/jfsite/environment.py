import os
from utils.pathtool import AddToPath, parentdir

local_dir = parentdir(os.path.abspath(__file__))

pt = AddToPath(local_dir)

pt.add(module='jfsite', uplev = 1)
pt.add(module='jflow', uplev = 2, down = ('src',))
pt.add(module='stdnet', uplev = 3, down = ('python-stdnet',))
pt.add(module='dynts', uplev = 3, down = ('dynts',))
pt.add(module='unuk', uplev = 3, down = ('unuk','src'))
pt.add(module='djpcms',uplev = 3, down = ('djpcms',))
pt.add(module='flowrepo',uplev = 3, down = ('django-flowrepo',))
pt.add(module='ccy', uplev = 3, down = ('ccy',))


def setup(setting_module):
    s2 = 'jfsite.allsettings.%s' % setting_module 
    os.environ['JFLOW_SETTINGS_MODULE']   = s2
    os.environ['STDNET_SETTINGS_MODULE']  = s2
    os.environ['UNUK_SETTINGS_MODULE']    = s2
    os.environ['DJANGO_SETTINGS_MODULE']  = s2
    

