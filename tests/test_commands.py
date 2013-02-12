import unittest

from docopt import docopt

from djset.commands import COMMAND, _parse_args, _create_djset
from djset.djset import DjSecret, DjConfig

from nose2.tools import params

class TestCommand(unittest.TestCase):
    
    def test_parse_argv(self):
        args = docopt(COMMAND % {'cmd':'test'}, argv=['add', 'key1=value1', '--global', '--settings=some.settings'])
        self.assertEqual(
            args,
            {'--global': True,
                '--name': None,
                '--settings': 'some.settings',
                '<key>': None,
                '<key>=<value>': 'key1=value1',
                'add': True,
                'remove': False}
        )
        

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
    