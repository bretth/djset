import os
import codecs

import keyring.util.platform
from keyring.py27compat import configparser
from keyring.backends.file import BaseKeyring
from keyring.core import load_keyring
from keyring.util.escape import escape as escape_for_ini
from keyring.util import properties


class UnencryptedKeyring(BaseKeyring):
    """
    UnencryptedKeyring is for storing settings which aren't sensitive.
    For convenience we use the same interface as a regular keyring.
    """
    
    filename = 'keyring_public.cfg'
 
    @properties.NonDataProperty
    def file_path(self):
        """
        The path to the file where passwords are stored. This property
        may be overridden by the subclass or at the instance level.
        """
        return os.path.join(keyring.util.platform.data_root(), self.filename)
    
    def encrypt(self, password):
        """Directly return the password itself.
        """
        return password

    def decrypt(self, password_encrypted):
        """Directly return encrypted password.
        """
        return password_encrypted
    
    def get_password(self, service, username):
        """Read the password from the file.
        """
        service = escape_for_ini(service)
        username = escape_for_ini(username)

        # load the passwords from the file
        config = configparser.RawConfigParser()
        if os.path.exists(self.file_path):
            config.read(self.file_path, encoding='utf-8')

        # fetch the password
        try:
            password = config.get(service, username)
        except (configparser.NoOptionError, configparser.NoSectionError):
            password = None
        
        return password

    def set_password(self, service, username, password):
        """Write the password in the file.
        """
        service = escape_for_ini(service)
        username = escape_for_ini(username)

        # ensure the file exists
        self._ensure_file_path()

        # load the keyring from the disk
        config = configparser.RawConfigParser()
        config.read(self.file_path)

        # update the keyring with the password
        if not config.has_section(service):
            config.add_section(service)
        config.set(service, username, password)

        # save the keyring back to the file
        config_file = codecs.open(self.file_path, 'w', 'utf-8')
        try:
            config.write(config_file)
        finally:
            config_file.close()
            
    def supported(self):
        """Applicable for all platforms, but do not recommend.
        """
        return 0


config_keyring = UnencryptedKeyring()