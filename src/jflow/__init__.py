'''Portfolio analysis'''
VERSION = (0, 4, 'a2')
 
def get_version():
    if len(VERSION) == 3:
        v = '%s.%s.%s' % VERSION
    else:
        v = '%s.%s' % VERSION[:2]
    return v
 
__version__ = get_version()
__license__  = "BSD"
__author__   = "Luca Sbardella"
__contact__  = "luca.sbardella@gmail.com"
__homepage__ = "http://github.com/lsbardel/jflow"


def install_libs():
    import os
    import sys
    path = os.path.join(os.path.split(os.path.abspath(__file__))[0],'libs')
    files = os.listdir(path)
    for dir in files:
        fullpath = os.path.join(path, dir)
        if os.path.isdir(fullpath):
            package = dir.split('-')[-1]
            try:
                __import__(package)
            except ImportError:
                sys.path.insert(0,fullpath)
            __import__(package)
            


def set_settings(setting_module):
    import os
    os.environ['JFLOW_SETTINGS_MODULE']   = setting_module
    os.environ['STDNET_SETTINGS_MODULE']  = setting_module
    os.environ['UNUK_SETTINGS_MODULE']    = setting_module
    os.environ['DJANGO_SETTINGS_MODULE']  = setting_module
            

install_libs()


def runtests(verbosity = 1, interactive = True,
             failfast = False, packages = None, extra_tests = None):
    from jflow.utils.tests import jFlowTestSuiteRunner
    packages = ['portfolio','instdata','trade','web'] if not packages else packages.split(' ')
    test_runner = jFlowTestSuiteRunner(verbosity = verbosity,
                                       interactive = interactive,
                                       failfast = failfast)
    return test_runner.run_tests(packages, extra_tests=extra_tests)



