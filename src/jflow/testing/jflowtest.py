import os
import sys
from unittest import TestLoader

__all__ = ['importall','installtests']

class importall(object):
    
    def __init__(self,package):
        if isinstance(package,str):
            package = __import__(package)
        self.imp(package)
            
    def imp(self, package):
        """
        Try recursively to import all subpackages under package.
        """
        package_name = package.__name__
        package_dir = os.path.dirname(package.__file__)
        for subpackage_name in os.listdir(package_dir):
            subdir = os.path.join(package_dir, subpackage_name)
            if not os.path.isdir(subdir):
                continue
            if not os.path.isfile(os.path.join(subdir,'__init__.py')):
                continue
            name = package_name+'.'+subpackage_name
            try:
                exec 'import %s as m' % (name)
            except Exception, msg:
                print 'Failed importing %s: %s' %(name, msg)
                continue
            self.handlemodule(m)
            self.imp(m)
    
    def handlemodule(self, m):
        pass



class installtests(importall):
    
    def __init__(self, package):
        self.loader = TestLoader()
        self.moduletests = {}
        super(installtests,self).__init__(package)
        
    
    def handlemodule(self, m):
        tests = self.loader.loadTestsFromModule(m)
        if tests._tests:
            self.loadtests(tests, m)
            
    def loadtests(self, tests, m):
        name = m.__name__
        te = self.moduletests.get(name,None)
        if te is None:
            self.moduletests[name] = tests