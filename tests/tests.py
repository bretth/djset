import os
import shutil
import time
import inspect
import unittest
from subprocess import call
from importlib import import_module
from tempfile import mkdtemp

import keyring
from keyring.errors import PasswordDeleteError
from keyring.py27compat import configparser
from keyring.util.escape import escape as escape_for_ini
from django.core.exceptions import ImproperlyConfigured

from nose2.tools import params

from djset.djset import DjSecret, DjConfig
from djset.commands import _parse_args, _create_djset
from djset.backends import UnencryptedKeyring, config_keyring
from djset.utils import _locate_settings


class BaseDjSecret(unittest.TestCase):

    def setUp(self):
        self.settings = 'tests.settings'
        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings
        from djset import DjSecret
        self.d = DjSecret()
        
class BaseDjSecretWithTeardown(BaseDjSecret):
    def tearDown(self):
        nsl = self.d.namespace('key')
        nsg = self.d.namespace('key', True)
        # osx and gnome don't provide an api for deleting passwords
        # but setting them to '' is sufficient.
        try:
            keyring.delete_password(nsl, 'key')
            keyring.delete_password(nsg, 'key')
        except PasswordDeleteError:  
            keyring.set_password(nsl, 'key', '')
            keyring.set_password(nsg, 'key', '')

        try:
            del os.environ['key']
        except KeyError:
            pass


class TestCommands(BaseDjSecret):

    def setUp(self):
        super(TestCommands, self).setUp()
        i = import_module(self.settings)
        self.f = inspect.getfile(i)
        
    
    def test_dexport(self):
        mtime1 = os.stat(self.f).st_mtime
        # due to random issues with warming mtime on OSX we'll call it twice and
        # put a sleep in the middle.
        call('source dexportunset.sh; dexport DJS=xyz', shell=True)
        time.sleep(1)  # HFS+ has a resolution of 1 sec
        call('source dexportunset.sh; dexport DJS=xyz', shell=True)
        mtime2 = os.stat(self.f).st_mtime
        
        self.assertNotEqual(mtime1, mtime2)
    
    def test_dunset(self):
        mtime1 = os.stat(self.f).st_mtime
        call('source dexportunset.sh; dunset DJS', shell=True)
        time.sleep(1)
        call('source dexportunset.sh; dunset DJS', shell=True)
        mtime2 = os.stat(self.f).st_mtime
        self.assertNotEqual(mtime1, mtime2)


class TestLocateSettings(BaseDjSecret):

    def test_locate_settings(self):
        s = _locate_settings()
        self.assertIn('tests/settings.py', s)


class TestNamespace(BaseDjSecret):
    
 
    @params(
        (False, 'tests.settings.keyring'),
        (True, 'key.keyring'))
    def test_namespace(self, glob, namespace):
        self.assertEqual(namespace, self.d.namespace('key', glob))

class TestSet(BaseDjSecretWithTeardown):
    
    @params(
        (False, u'value'),
        (True, u'global-value'),
    )
    def test_set(self, glob, value):
        self.d.set('key', value, glob)
        ns = self.d.namespace('key', glob)
        v = keyring.get_password(ns, 'key')
        self.assertEqual(value, v)
        

class TestGet(BaseDjSecretWithTeardown):
    
    def setUp(self):
        super(TestGet, self).setUp()
        # override user input function for test
        self.d._prompt_for_value = lambda key, prompt_default, prompt_help: 'vp'
        self.d.prompt = True
    
    @params(
        # env, local, global, result
        (u'v', u'vl', u'vg', u'v'),
        ('', u'vl', u'vg', u'vl'),
        ('', '', u'vg', u'vg'),
        ('', '', '', 'vp'),
    )
    def test_get_with_prompt(self, env, local, glob, result):    
        if env:
            os.environ['key'] = env
        if local:
            self.d.set('key', local)
        if glob:
            self.d.set('key', glob, True)
        self.assertEqual(result, self.d.get('key'))


class TestGetNoPrompt(BaseDjSecret):

    def test_get_no_prompt(self):
        with self.assertRaises(ImproperlyConfigured):
            self.d.get('key')
    
    

class TestRemove(BaseDjSecretWithTeardown):
    
    def setUp(self):
        super(TestRemove, self).setUp()
        self.d.set('key', 'value')
        self.d.set('key', 'value', True)
        
    @params(False, True)
    def test_remove(self, glob):
        self.d.remove('key', glob)
        ns = self.d.namespace('key', glob)
        self.assertEqual(keyring.get_password(ns, 'key'), '')
        
class TestParseArgs(unittest.TestCase):
    
    
    add = {'--global': False,
    '<key>': None, #remove
    '<key>=<value>': 'key=value', #add
    'add': True,
    'remove': False}
    add_result = {
        'func': 'set',
        'args': ('key', 'value'),
        'kwargs': {'glob': False},
        }

    add_global = {'--global': True,
    '<key>': None, #remove
    '<key>=<value>': 'key=value', #add
    'add': True,
    'remove': False}
    add_global_result = {
        'func': 'set',
        'args': ('key', 'value'),
        'kwargs': {'glob': True},        
    }
    add_name = {'--global': True,
    '--name': 'djstest',
    '<key>': None, #remove
    '<key>=<value>': 'key=value', #add
    'add': True,
    'remove': False}
    add_name_result = {'func': 'set',
        'args': ('key', 'value'),
        'kwargs': {'glob': True},
    }
    
    add_invalid = {'--global': False,
    '<key>': None, #remove
    '<key>=<value>': 'key=', #add
    'add': True,
    'remove': False}
    add_invalid_result = None
    
    remove = {'--global': False,
    '<key>': 'key', #remove
    '<key>=<value>': None, #add
    'add': False,
    'remove': True}
    remove_result = {
        'func': 'remove',
        'args': ('key', ),
        'kwargs': {'glob': False},
    }
    
    
    @params(
        (add, add_result),
        (add_global, add_global_result),
        (add_name, add_name_result),
        (add_invalid, add_invalid_result),
        (remove, remove_result),
    )
    def test_parse_args(self, args, result):
        func, args, kwargs = _parse_args(args, DjSecret)
        if not func:
            self.assertEqual(func, result)
        else:
            self.assertEqual(func.__name__, result['func'])
            self.assertEqual(args, result['args'])
            self.assertEqual(kwargs, result['kwargs'])
    
    @params(DjSecret, DjConfig)
    def test_create_djset(self, cls):
        args = {'--global': True,
        '--name': 'djstest',
        '<key>': None, #remove
        '<key>=<value>': 'key=value', #add
        'add': True,
        'remove': False}
        d = _create_djset(args, cls)
        self.assertEqual(d.name, 'djstest')


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
    
    
        
    
