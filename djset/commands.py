
from docopt import docopt
import os
import sys

from .djset import DjSecret, DjConfig
from .utils import _locate_settings

COMMAND = """
Usage:  dj%s add <key>=<value> [--global] [--name=<name> | --settings=<settings>]
        dj%s remove <key> [--global] [--name=<name> | --settings=<settings>]

"""


def _create_djset(args, cls):
    """ Return a DjSecret object """
    name = args.get('--name')
    settings = args.get('--settings')
    if name:
        return cls(name=name)
    elif settings:
        return cls(name=settings)
    else:
        return cls() 


def _parse_args(args, cls):
    """ Parse a docopt dictionary of arguments """
    
    d = _create_djset(args, cls)
    
    key_value_pair = args.get('<key>=<value>')
    key = args.get('<key>')
    func = None
    if args.get('add') and key_value_pair:
        fargs = tuple(args.get('<key>=<value>').split('='))
        if fargs[1]:
            func = d.set
    elif args.get('remove') and key:
        func = d.remove
        fargs = (args.get('<key>'),)
    kwargs = {'glob': args.get('--global')}
    if func:
        return func, fargs, kwargs
    else:
        return None, None, None

def main(command, cls):
    sys.path.append(os.getcwd())
    args = docopt(command)
    func, fargs, kwargs = _parse_args(args, cls)
    if func:
        func(*fargs, **kwargs)
        s = _locate_settings(args.get('--settings'))
        os.utime(s, None)

def djsecret():
    command = COMMAND % 'secret'
    main(command, DjSecret)
    
     
def djconfig():
    command = COMMAND % 'config'
    main(command, DjConfig)

        
    
    
