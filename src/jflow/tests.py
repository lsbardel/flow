
# Install jflow if not already installed
from _legacy import quickutils
putils  = quickutils.PackageInstaller(__file__)
putils.install('jflow', up = 1, addname = False)

from unittest import TestResult, TextTestRunner

from jflow.testing import installtests

import jflow.core as core


def run():
    runner = TextTestRunner()
    tests = installtests(core).moduletests

    for k,suite in tests.items():
        runner.run(suite)
        #print "Running %s" % k
        #result = TestResult()
        #suite.run(result)
        #print result
        
        
if __name__ == '__main__':
    run()
