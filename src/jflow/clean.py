


if __name__ == '__main__':
    import os
    from utils.files import rmfiles
    path = os.curdir
    removed, allfiles = rmfiles(path,'pyc')
    print 'removed %s pyc files out of %s' % (removed, allfiles)