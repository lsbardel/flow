import environment
import jflow
jflow.set_settings('jfsite.allsettings.test')

from jflow.utils.tests import jFlowTestSuiteRunner, defaultTestLoader
from stdnet import tests

def run(packages = None):
    tests = None
    jflow.runtests(packages = packages, extra_tests = tests)
    

