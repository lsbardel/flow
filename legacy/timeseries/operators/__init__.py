
import baseoper as base

__all__ = ['get','all','unwind']

unwind = base.unwind

def get(code, retval = None):
    autodiscover()
    return base.get(code, retval = retval)

def all():
    autodiscover()
    return base._operators
    


def autodiscover():
    global _discovered;
    if _discovered:
        return
    _discovered = True
    imported = {'__init__':True, 'base': True}
    import os
    path  = os.path.dirname(__file__)
    files = os.listdir(path)
    for f in files:
        name = f.split('.')[0]
        if imported.get(name,None) == None:
            try:
                __import__(name,globals(),locals(),[''])
                imported[name] = True
            except Exception, e:
                imported[name] = False
            



_discovered = False