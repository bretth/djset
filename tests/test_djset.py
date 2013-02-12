import os
import time
import inspect
import unittest
from subprocess import call
from importlib import import_module


import keyring
from keyring.errors import PasswordDeleteError
from django.core.exceptions import ImproperlyConfigured
from nose2.tools import params

from djset.djset import DjSecret
from djset.utils import _locate_settings


class BaseDjSecret(unittest.TestCase):

    def setUp(self):
        self.settings = 'tests.settings'
        os.environ['DJANGO_SETTINGS_MODULE'] = self.settings
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





