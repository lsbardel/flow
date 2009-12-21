
import os
from files import fullsplit

__all__ = ['getPackages','getExtensions']


def getPackages(root):
    # Compile the list of packages available, because distutils doesn't have
    # an easy way to do this.
    
    if os.path.isdir(root):
        
        packages, data_files = [], []
        
        for dirpath, dirnames, filenames in os.walk(root):
            
            # Ignore dirnames that start with '.'
            for i, dirname in enumerate(dirnames):
                if dirname.startswith('.'):
                    del dirnames[i]
            
            if '__init__.py' in filenames:
                packages.append('.'.join(fullsplit(dirpath)))
            elif filenames:
                data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
        
        return packages, data_files
    
    else:
        raise ValueError
    
    
def getExtensions(dir, extens = None):
    """
    Get all extensions
    """
    if extens == None:
        extens = ('c','cc','cpp')
    extensions = []
    
    
    files = os.listdir(dir)
    for f in files:
        fullpath = os.path.join(dir,f)
        if os.path.isdir(fullpath):
            extensions.extend(getExtensions(fullpath,extens))
        else:
            sp = f.split('.')
            N  = len(sp)
            if N > 1 and sp[N-1] in extens:
                extensions.append(fullpath)                    
    return extensions

