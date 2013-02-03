
"""
Usage:  djset add <key>=<value> [--global] [--name]
        djset remove <key> [--global] [--name]

"""
from .djset import DjSet

def _create_djset(args):
    """ Return a DjSet object """
    name = args.get('--name')
    if name:
        return DjSet(name)
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
    args = docopt(__doc__)
    
    func, args, kwargs = _parse_args(args)
    if func:
        func(*args, **kwargs)
    
    
