import os
import unittest
import types

from environment import setup
setup('tests')

from stdnet import tests
#from jflow import tests as ptests

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
    suite  = loader.loadTestsFromModules(tests)
    #suite  = loader.loadTestsFromModules(ptests)
    #suite  = loader.loadTestsFromModules(tests,ptests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
        
        
if __name__ == '__main__':
    run()

