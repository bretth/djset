import os
import time
import inspect
import unittest
from subprocess import call
from importlib import import_module

import keyring
from keyring.errors import PasswordDeleteError
from nose2.tools import params
from django.core.exceptions import ImproperlyConfigured

from djset.djset import _locate_settings
from djset.command import _parse_args, _create_djset
from djset import DjSet



class BaseDjSet(unittest.TestCase):

    def setUp(self):
        self.settings = 'tests.settings'
        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings
        self.d = DjSet()
        
class BaseDjSetWithTeardown(BaseDjSet):
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


class TestCommands(BaseDjSet):

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


class TestLocateSettings(BaseDjSet):

    def test_locate_settings(self):
        s = _locate_settings()
        self.assertIn('tests/settings.py', s)


class TestNamespace(BaseDjSet):
    
 
    @params(
        (False, 'key.tests.settings.keyring'),
        (True, 'key.keyring'))
    def test_namespace(self, glob, namespace):
        self.assertEqual(namespace, self.d.namespace('key', glob))

class TestSet(BaseDjSetWithTeardown):
    
    @params(
        (False, u'value'),
        (True, u'global-value'),
    )
    def test_set(self, glob, value):
        self.d.set('key', value, glob)
        ns = self.d.namespace('key', glob)
        v = keyring.get_password(ns, 'key')
        self.assertEqual(value, v)
        

class TestGet(BaseDjSetWithTeardown):
    
    def setUp(self):
        super(TestGet, self).setUp()
        # override user input function for test
        self.d._prompt_for_value = lambda key, prompt_default: 'vp'
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


class TestGetNoPrompt(BaseDjSet):

    def test_get_no_prompt(self):
        with self.assertRaises(ImproperlyConfigured):
            self.d.get('key')
    
    

class TestRemove(BaseDjSetWithTeardown):
    
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
        func, args, kwargs = _parse_args(args)
        if not func:
            self.assertEqual(func, result)
        else:
            self.assertEqual(func.__name__, result['func'])
            self.assertEqual(args, result['args'])
            self.assertEqual(kwargs, result['kwargs'])
            
    def test_create_djset(self):
        args = {'--global': True,
        '--name': 'djstest',
        '<key>': None, #remove
        '<key>=<value>': 'key=value', #add
        'add': True,
        'remove': False}
        d = _create_djset(args)
        self.assertEqual(d.name, 'djstest')
          
