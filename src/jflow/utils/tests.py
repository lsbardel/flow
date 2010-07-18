import unittest
from django.test import TestCase
from django.db.models import get_app, get_apps
from django.test.simple import DjangoTestSuiteRunner, reorder_suite, get_tests
from django.contrib.contenttypes.models import ContentType

from stdnet import orm


class jFlowTest(TestCase):
    loadonce = False
    
    def __init__(self,*args,**kwargs):
        self.started = False
        super(jFlowTest,self).__init__(*args,**kwargs)
        
    def setUp(self):
        if not self.loadonce:
            self.initialize()
            
    def initialize(self):
        pass
        
    def _pre_setup(self):
        if not self.loadonce:
            self._pre_setup_real()
    
    def _pre_setup_real(self):
        super(jFlowTest,self)._pre_setup()
        
    def _post_teardown(self):
        orm.clearall()
        if not self.loadonce:
            self._post_teardown_real()
    
    def _post_teardown_real(self):
        super(jFlowTest,self)._post_teardown()
    
        

class jFlowTestSuite(unittest.TestSuite):
    '''A specialized test suite'''
    
    def __init__(self, *args, **kwargs):
        self.testCaseClass = None
        super(jFlowTestSuite,self).__init__(*args, **kwargs)
        
    def addTest(self, test):
        if isinstance(test,jFlowTest):
            name = test.__class__.__name__
            if self.testCaseClass is None:
                self.testCaseClass = name
            elif self.testCaseClass != name:
                self.testCaseClass = False
        super(jFlowTestSuite,self).addTest(test)
            
    def run(self, result):
        if self.testCaseClass:
            first = True
            test  = None
            for test in self._tests:
                if result.shouldStop:
                    test = None
                    break
                if first:
                    first = False
                    if test.loadonce:
                        test._pre_setup_real()
                        test.initialize()
                test(result)
            if test and test.loadonce:
                test._post_teardown_real()
            return result
        else:
            return super(jFlowTestSuite,self).run(result)


defaultTestLoader = unittest.TestLoader()
defaultTestLoader.suiteClass = jFlowTestSuite


def build_suite(app_module):
    test_module = get_tests(app_module)
    if test_module:
        # Load unit and doctests in the tests.py module. If module has
        # a suite() method, use it. Otherwise build the test suite ourselves.
        if hasattr(test_module, 'suite'):
            suite = test_module.suite()
        else:
            suite = jFlowTestSuite()
            suite.addTest(defaultTestLoader.loadTestsFromModule(test_module))
    return suite
    


class jFlowTestSuiteRunner(DjangoTestSuiteRunner):
    
    def setup_databases(self, **kwargs):
        old_names, mirrors = super(jFlowTestSuiteRunner,self).setup_databases(**kwargs)
        #ContentType.objects.all().delete()
        #from django.core.management import call_command
        #call_command('loaddata', 'content_types', verbosity=self.verbosity)
        return old_names, mirrors
    
    def build_suite(self, test_labels, extra_tests=None, **kwargs):
        suite = jFlowTestSuite()

        if test_labels:
            for label in test_labels:
                if '.' in label:
                    suite.addTest(build_test(label))
                else:
                    app = get_app(label)
                    suite.addTest(build_suite(app))
        else:
            for app in get_apps():
                suite.addTest(build_suite(app))

        if extra_tests:
            for test in extra_tests:
                suite.addTest(test)

        return suite
        #return reorder_suite(suite, (TestCase,))
    