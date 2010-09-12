import unittest

import jflow


class TestInitFile(unittest.TestCase):

    def test_version(self):
        self.assertTrue(jflow.VERSION)
        self.assertTrue(jflow.__version__)
        self.assertEqual(jflow.__version__,jflow.get_version())
        self.assertTrue(len(jflow.VERSION) >= 2)

    def test_meta(self):
        for m in ("__author__", "__contact__", "__homepage__", "__doc__"):
            self.assertTrue(getattr(jflow, m, None))