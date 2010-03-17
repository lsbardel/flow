'''
qutils is a small collection of utilities for administering
a python project on the fly
'''
import os
import sys
import _json as json

class PackageInstaller(object):
    '''
    Install packages on the fly
    '''
    def __init__(self, file = None):
        self.locdir = os.getcwd()
        if file:
            self.dir = os.path.dirname(file)
            self.dir = self.dir or self.locdir
        else:
            self.dir = self.locdir
        
    def install(self, name, up = None, addname = True, *args):
        try:
            p = __import__(name, globals(), locals(), [''])
        except ImportError:
            p = self._install(name, up, addname, *args)
        return p.__path__[0]
            
    def parentdirectory(self, up = 1):
        if not up:
            return self.dir
        os.chdir(self.dir)
        for l in range(0,up):
            os.chdir(os.pardir)
        path = os.getcwd()
        os.chdir(self.locdir)
        return path
    
    def directory(self, *args, **kwargs):
        up = kwargs.pop('up',0)
        path = self.parentdirectory(up)
        if args:
            path = os.path.join(path,*args)
        return path
            
    def _install(self, name, up, addname, *args):
        if addname:
            args += (name,)
        path = self.directory(up = up, *args)
        if path not in sys.path:
            sys.path.insert(0,path)
        return __import__(name,globals(),locals(),[''])
    
    def adddir(self, base, *args):
        path = os.path.join(base, *args)
        if path not in sys.path:
            sys.path.insert(0,path)
        return path
    
    
def open_file(path, file, typ = 'w'):
    pf = os.path.join(path,file)
    try:
        io1 = open(pf,typ)
    except Exception, e:
        raise IOError, 'Could not open file %s. %s' % (pf,e)
    return io1


def check_file(path, file, typ = 'w'):
    r = open_file(path, file, typ)
    return r


def listdir(path, extension = None):
    files = os.listdir(path)
    if extension:
        nfiles = []
        ext = str(extension).lower()
        for f in files:
            sf = f.split('.')
            if len(sf) == 2:
                if sf[1] == ext:
                    nfiles.append(f)
        return nfiles
    else:
        return files

def rmgeneric(path, __func__):
    try:
        __func__(path)
        #print 'Removed ', path
        return 1
    except OSError, (errno, strerror):
        print 'Could not remove %s, %s' % (path,strerror)
        return 0
        

def rmfiles(path, ext = None):    
    if not os.path.isdir(path):
        return 0
    trem = 0
    tall = 0
    files = os.listdir(path)
    for f in files:
        fullpath = os.path.join(path, f)
        if os.path.isfile(fullpath):
            sf = f.split('.')
            if len(sf) == 2:
                if ext == None or sf[1] == ext:
                    tall += 1
                    trem += rmgeneric(fullpath, os.remove)
        elif os.path.isdir(fullpath):
            r,ra = rmfiles(fullpath, ext)
            trem += r
            tall += ra
    return trem, tall


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



def packages_in_dirs(root_dir, *package_names):
    '''
    Ignore dirnames that start with '.'
    '''
    packages, data_files = [], []
    
    pieces = fullsplit(root_dir)
    if pieces[-1] == '':
        len_root_dir = len(pieces) - 1
    else:
        len_root_dir = len(pieces)
    
    for package_name in package_names:
        package_dir = os.path.join(root_dir, package_name)
    
        for dirpath, dirnames, filenames in os.walk(package_dir):
            for i, dirname in enumerate(dirnames):
                if dirname.startswith('.'): del dirnames[i]
            if '__init__.py' in filenames:
                packages.append('.'.join(fullsplit(dirpath)[len_root_dir:]))
            elif filenames:
                data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
    
    return packages, data_files


def get_version(version_tuple):
    if version_tuple[2] is not None:
        v = '%s.%s %s' % version_tuple
    else:
        v = '%s.%s' % version_tuple[:2]
    return v


if __name__ == '__main__':
    if len(sys.argv) > 1:
        com = sys.argv[1]
        if com == 'clean':
            path = os.curdir
            removed, allfiles = rmfiles(path,'pyc')
            print 'removed %s pyc files out of %s' % (removed, allfiles)

