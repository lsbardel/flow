#
# Requires pytz 2008i or higher
#
try:
    from pytz import *
except:
    err = ["Cannot load package pytz, World Timezone Definitions for Python",
           "You can obtain it at http://pytz.sourceforge.net/"]
    raise ImportError, '\n'.join(err)

def make_countries():
    v = {}
    for k,n in country_names.items():
        v[u'%s'% k.upper()] = u'%s' % n
    v.pop('GB')
    v['EU'] = 'Eurozone'
    v['UK'] = 'United Kingdom'
    v['PX'] = 'Pacific ex Japan'
    v['PP'] = 'Pacific Rim'
    v['WW'] = 'World'
    v['LM'] = 'Latin America'
    return v



def dump(filename = 'countries.csv'):
    cs = make_countries()
    f = open(filename,'w')
    l = []
    for v in cs.items():
        l.append('%s,%s' % v)
    data = '\n'.join(l)
    f.write(data)
    f.close()
    
