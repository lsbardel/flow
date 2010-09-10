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


