
import os



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
    