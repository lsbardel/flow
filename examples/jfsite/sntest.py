import os
import unittest
import types

import environment
environment.setup('test')

packages = ['jflow.db.portfolio',
            'jflow.db.instdata']

from jflow.utils.tests import jFlowTestSuiteRunner, defaultTestLoader
from stdnet import tests
from jflow import tests as ptests

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


def run(verbosity = 1, interactive = True, failfast = False):
    test_runner = jFlowTestSuiteRunner(verbosity = verbosity, interactive = interactive, failfast = failfast)
    extra_tests = None
    return test_runner.run_tests(packages, extra_tests=extra_tests)


    runner = jFlowTestSuite()
    suite.run()
    loader = TestLoader()
    #suite  = loader.loadTestsFromModules(tests)
    suite  = loader.loadTestsFromModules(ptests)
    #suite  = loader.loadTestsFromModules(tests,ptests)
    runner = unittest.TextTestRunner()
    runner.run(suite)
        
        
if __name__ == '__main__':
    run()

