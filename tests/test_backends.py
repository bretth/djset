
import os
import unittest
import shutil
from tempfile import mkdtemp

from keyring.py27compat import configparser

from djset.backends import config_keyring


class UEBackendBase(unittest.TestCase):
    
    def setUp(self):
        self.keyring = config_keyring
        self.tmpdir = mkdtemp()
        self.filename = 'config_keyring.cfg'
        self.file_path = os.path.join(self.tmpdir, self.filename)
        # alter the filepath so we're not using the real one
        config_keyring.file_path = self.file_path

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


class TestUESet(UEBackendBase):

    def test_set_password(self):
        self.keyring.set_password('test', 'key', 'value')
        # load the passwords from the file
        config = configparser.RawConfigParser()
        config.read(self.file_path, encoding='utf-8')
        value = config.get('test', 'key')
        self.assertEqual(value, 'value')


class TestUEGet(UEBackendBase):

    def setUp(self):
        super(TestUEGet, self).setUp()
        self.keyring.set_password('test', 'key', 'value')

    def test_get_password(self):
        self.assertEqual(self.keyring.get_password('test', 'key'), 'value')