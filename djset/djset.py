
import os

import keyring
from keyring.errors import PasswordDeleteError
from django.core.exceptions import ImproperlyConfigured


class DjSet(object):
    
    _glob = 'keyring'
    
    def __init__(self, name='', prompt=False):
        self.settings = os.environ['DJANGO_SETTINGS_MODULE']
        self.name = name or self.settings
        self.prompt = prompt
                
    def _prompt_for_value(self, key):
        try:
            input = raw_input
        except NameError: # py3
            pass
        return input('Enter the %s value for %s []:' % (self.settings, key))
    
    
    def namespace(self, key, glob=False):
        """Return a namespace for keyring"""
        ns = '.'.join([key, self._glob]) if glob else '.'.join([key, self.name, self._glob])
        return ns
    
    def get(self, key, default=None):
        """
        Return the value for key from the environment or keyring.
        The keyring value is resolved from a local namespace or a global one.
        """
        value = os.getenv(key)
        if not value:
            value = keyring.get_password(self.namespace(key), key)
        if not value:
            value = keyring.get_password(self.namespace(key, glob=True), key)
        value = value or default
        if not value and not self.prompt:
            error_msg = "The %s setting is undefined in the environment and %s" % (value, self._glob)
            raise ImproperlyConfigured(error_msg)
        elif not value and self.prompt:
            value = self._prompt_for_value(key)
        return value
    
    def set(self, key, value, glob=False):
        """Set the key value pair in a local or global namespace"""
        ns = self.namespace(key, glob)
        keyring.set_password(ns, key, value)
    
    def remove(self, key, glob=False):
        """Remove key value pair in a local or global namespace."""
        ns = self.namespace(key, glob)
        try:
            keyring.delete_password(ns, key)
        except PasswordDeleteError:  # OSX and gnome have no delete method 
            self.set(key, '', glob)

    
def _locate_settings(settings=''):
    "Return the path to the DJANGO_SETTINGS_MODULE"
    
    import imp
    import sys
    sys.path.append(os.getcwd())
    settings = settings or os.getenv('DJANGO_SETTINGS_MODULE')
    if settings:
        parts = settings.split('.')
        f = imp.find_module(parts[0])[1]
        args = [f] + parts[1:]
        path = os.path.join(*args)
        path = path + '.py'
        if os.path.exists(path):
            return path


def locate_settings():
    "Print the path to your DJANGO_SETTINGS_MODULE"
    
    settings = _locate_settings()
    if settings:
        print(settings)