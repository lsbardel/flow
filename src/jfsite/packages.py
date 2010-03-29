'''
Install Packages.
This is usually needed during development
'''
import os
import sys
from django.utils.importlib import import_module

def backdir(path, n):
    if n:
        return backdir(os.path.split(path)[0],n-1)
    else:
        return path
    
def add2path(name, path):
    try:
        import_module(name)
    except:
        if os.path.exists(path) and path not in sys.path:
            sys.path.append(path)

def install():
    dir     = os.path.dirname(__file__)
    path    = backdir(dir,1)
    if path not in sys.path:
        sys.path.append(path)
    
    base    = backdir(path,2)
    add2path('djpcms', os.path.join(base,'djpcms'))
    add2path('ccy', os.path.join(base,'ccy'))
    add2path('tagging', os.path.join(base,'django-tagging'))
     
    # Try to import. If failed throw the error
    import jfsite as site
    
    # machines module is not provided for obvious security reasons.
    # machines_example is provided for illustration
    try:
        import machines
    except ImportError:
        import machines_test as machines
    
    # Get server setting
    sett    = machines.get_machine(site.__path__[0])
    # Set identity
    sett.id = machines.Identity()
    
    return sett
