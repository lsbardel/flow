import os
import unittest
import settings
import types
from django.core.management import setup_environ

os.environ['JFLOW_SETTINGS_MODULE'] = 'jflow.jfsite.allsettings.tests'
os.environ['STDNET_SETTINGS_MODULE'] = 'jflow.jfsite.allsettings.tests'

setup_environ(settings)

from stdnet import tests
from jflow.db.portfolio import tests as ptests

class TestLoader(unittest.TestLoader):
    
    def loadTestsFromModules(self, *modules):
        """Return a suite of all tests cases contained in the given module"""
        tests = []
        for module in modules:
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, (type, types.ClassType)) and
                    issubclass(obj, unittest.TestCase)):
                    tests.append(self.loadTestsFromTestCase(obj))
        return self.suiteClass(tests)


def run():
    loader = TestLoader()
    #suite  = loader.loadTestsFromModules(tests)
    suite  = loader.loadTestsFromModules(ptests)
    #suite  = loader.loadTestsFromModules(tests,ptests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
        
        
if __name__ == '__main__':
    run()

