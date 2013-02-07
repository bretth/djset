
"""
Usage:  djset add <key>=<value> [--global] [--name=<name> | --settings=<settings>]
        djset remove <key> [--global] [--name=<name> | --settings=<settings>]

"""
from .djset import DjSet, _locate_settings

def _create_djset(args):
    """ Return a DjSet object """
    name = args.get('--name')
    settings = args.get('--settings')
    if name:
        return DjSet(name=name)
    elif settings:
        return DjSet(name=settings)
    else:
        return DjSet() 


def _parse_args(args):
    """ Parse a docopt dictionary of arguments """
    
    d = _create_djset(args)
    
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


def main():
    from docopt import docopt
    import os
    import sys
    #for p in sys.path: print(p)
    sys.path.append(os.getcwd())
    args = docopt(__doc__)
    func, fargs, kwargs = _parse_args(args)
    if func:
        func(*fargs, **kwargs)
        s = _locate_settings(args.get('--settings'))
        os.utime(s, None)
        
    
    
