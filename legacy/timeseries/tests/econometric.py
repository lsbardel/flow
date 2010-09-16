import unittest

import data

    
    

class MultivariateTest(unittest.TestCase):
    
    def setUp(self):
        self.beta = ny.array([2.0,-10.0,100.0])
        x    = data.get_multivariate(N = 2)
        x.addconstant(1)
        self.data = self.data.prod(self.beta).tovector().addts(x).tomatrix()
        
    def testols(self):
        '''
        Test Ordinary Least Squares algorithm
        '''
        res = self.data.econometric.ols()
        for i in range(0,len(self.beta)):
            self.assertAlmostEqual(res[i])
        
        
        