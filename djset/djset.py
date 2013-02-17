
import os

import keyring
from keyring.errors import PasswordDeleteError
from django.core.exceptions import ImproperlyConfigured

from .backends import config_keyring


class DjBase(object):

    _glob = 'keyring'
    keyring = keyring
    raise_on_none = None
    
    def __init__(self, prompt=False, name=''):
        self.name = name
        self.prompt = prompt
                
    def _prompt_for_value(self, key, prompt_default, prompt_help=''):
        try:
            input = raw_input
        except NameError: # py3
            pass
        if prompt_help:
            print(prompt_help, os.linesep)
        return input("Enter the '%s' value for %s [%s]:" % (self.name, key, prompt_default)) or prompt_default
    
    def namespace(self, key, glob=False):
        """Return a namespace for keyring"""
        if not self.name:
            self.name = os.environ['DJANGO_SETTINGS_MODULE'] 
        ns = '.'.join([key, self._glob]) if glob else '.'.join([self.name, self._glob])
        return ns
    
    def get(self, key, prompt_default='', prompt_help=''):
        value = os.getenv(key)
        if not value:
            value = self.keyring.get_password(self.namespace(key), key)
        if not value:
            value = self.keyring.get_password(self.namespace(key, glob=True), key)
        if not value and self.prompt:
            value = self._prompt_for_value(key, prompt_default, prompt_help)
            if value:
                self.set(key, value)
        return value
    
    def set(self, key, value, glob=False):
        """Set the key value pair in a local or global namespace"""
        ns = self.namespace(key, glob)
        self.keyring.set_password(ns, key, value)
    
    def remove(self, key, glob=False):
        """Remove key value pair in a local or global namespace."""
        ns = self.namespace(key, glob)
        try:
            self.keyring.delete_password(ns, key)
        except PasswordDeleteError:  # OSX and gnome have no delete method 
            self.set(key, '', glob)


class DjConfig(DjBase):
    """
    DjConfig uses a config style file to store settings that are not sensitive secrets.
    """
    keyring = config_keyring


class DjSecret(DjBase):
    """
    DjSecret uses the preferred and available keyring for your OS to set and
    get secrets if the secret is not in the env. If no secret is found,
    it can either prompt for input or raise a ImproperlyConfigured error.
    """
    raise_on_none = ImproperlyConfigured
   
    def get(self, key, prompt_default=''):
        """
        Return the value for key from the environment or keyring.
        The keyring value is resolved from a local namespace or a global one.
        """
        value = super(DjSecret, self).get(key, prompt_default)
        if not value and not self.prompt and self.raise_on_none:
            error_msg = "The %s setting is undefined in the environment and djset %s" % (key, self._glob)
            raise self.raise_on_none(error_msg)
        elif not value and self.prompt:
            value = self._prompt_for_value(key, prompt_default)
            if value:
                self.set(key, value)
        return value



    
