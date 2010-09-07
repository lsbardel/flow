import os
from utils.pathtool import AddToPath, parentdir

local_dir = parentdir(os.path.abspath(__file__))

pt = AddToPath(local_dir)

pt.add(module='djpcms',uplev = 3, down = ('djpcms',))
pt.add(module = 'ccy', uplev = 3, down = ('ccy',))

