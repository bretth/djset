import os
import unittest

from djset.utils import getbool

from nose2.tools import params

class TestGetBool(unittest.TestCase):
    
    @params(('1', True), ('True', True), ('False', False), ('0', False), ('b', False), ('', False))
    def test_get_bool(self, arg, result):
        os.environ['tgb'] = arg
        value = getbool('tgb')
        self.assertEqual(value, result)
        
    
