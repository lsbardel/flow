import os
import sys
from distutils.command.install import INSTALL_SCHEMES
from distutils.core import setup
 
# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']
    
    
package_name = 'jflow'
root_dir     = os.path.join(os.path.dirname(__file__),'src')
package_dir  = os.path.join(root_dir, package_name)
 
def get_version():
    if root_dir not in sys.path:
        sys.path.insert(0,root_dir)
    import jflow
    return jflow.get_version()
 
 
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
 
def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)
 
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
def get_rel_dir(d,base,res=''):
    if d == base:
        return res
    br,r = os.path.split(d)
    if res:
        r = os.path.join(r,res)
    return get_rel_dir(br,base,r)

packages, data_files = [], []
pieces = fullsplit(root_dir)
if pieces[-1] == '':
    len_root_dir = len(pieces) - 1
else:
    len_root_dir = len(pieces)
 
for dirpath, dirnames, filenames in os.walk(package_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))
    elif filenames:
        rel_dir = get_rel_dir(dirpath,root_dir)
        data_files.append([rel_dir, [os.path.join(dirpath, f) for f in filenames]])

if os.name == 'nt':
    lib_dir = os.path.join(package_dir,'lib')
    libs = ['_jflib.pyd','blas.dll','boost_python.dll','lapack.dll']
    rel_dir = get_rel_dir(lib_dir,root_dir)
    data_files.append([rel_dir, [os.path.join(lib_dir, f) for f in libs]])
 

setup(
        name         = package_name,
        version      = get_version(),
        author       = 'Luca Sbardella',
        author_email = 'luca.sbardella@gmail.com',
        url          = 'http://github.com/lsbardel/jflow',
        license      = 'BSD',
        description  = 'Quantitative finance and econometric analysis',
        long_description = read('README.rst'),
        packages     = packages,
        package_dir  = {'': 'src'},
        data_files   = data_files,
        install_requires = ['ccy>=0.3.2',
                            'dynts',
                            'python-stdnet',
                            'unuk',
                            'django-extracontent'],
        classifiers = [
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Plugins',
            'Intended Audience :: Developers',
            'Intended Audience :: Financial and Insurance Industry',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Utilities'
        ],
    )
 