VERSION = (0, 2, 0)


def get_version():
    version = '%s.%s' % (VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '%s.%s' % (version, VERSION[2])
    #from django.utils.version import get_svn_revision
    #svn_rev = get_svn_revision()
    #if svn_rev != u'SVN-unknown':
    #    version = "%s %s" % (version, svn_rev)
    return version


__version__ = get_version()