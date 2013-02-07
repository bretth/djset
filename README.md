Djset
=====

Djset simplifies managing secrets in your django settings.

A common django configuration pattern is to use environment variables in production environments with a local unversioned settings file to hold your secret development api keys and other settings. Djset simplifies management of secret settings locally by using the shell environ, system keyring, and optionally user prompted settings.

Djset is a convenience layer on top of the python keyring library.


Installation
---------------

Djset currently requires python >= 2.6. There are currently some outstanding issues with python keyring on python 3.


``pip install djset``

To install the optional environment variable helpers (in OSX or Linux) put ``source dexportunset.sh`` in your postactivate script if you use virtualenvwrapper or in your shell startup file if you don't.

Djset is entirely dependent on the DJANGO_SETTINGS_MODULE variable being set in the environment. You can use the virtualenvwrapper postactivate and postdeactivate scripts to export and unset this variable for your project.


Usage
--------
Add a setting you want kept secret from the command line:

    djset add SECRET_KEY=xyz    

In your settings.py add something like the following:

        from djset import DjSet
        
        s = DjSet(prompt=True)
        SECRET_KEY = s.get('SECRET_KEY')  

The key is resolved in the following order:

        environment
            |
        keychain in the KEY.NAME.keyring namespace (local)
            |
        keychain in the KEY.keyring namespace (global)
            |
        prompt for input or raise ImproperlyConfigured
        
Prompt will also *add* the key to your keyring. You may want to do something like ``s = DjSet(DEBUG)`` to prompt for settings in the local environment and raise an error in production.

A common practice is to set some sensible defaults for development including for example your SECRET_KEY. One way this can be done is an *if else* pattern in your settings. Djset provides for this with a twist on the the .get behaviour which is not the same as the dictionary method.

``SECRET_KEY = s.get('SECRET_KEY', prompt_default='xyz')`` or just ``SECRET_KEY = s.get('SECRET_KEY', 'xyz')`` will set the default value the user is prompted with, but if prompt=False will still raise an ImproperlyConfigured error. The point of this is to avoid pushing local development secrets into production.

By default the *NAME* in the namespace is your DJANGO_SETTINGS_MODULE. To use an alternate namespace: 

	s = DjSet(name='your.settings')

To add and remove keys use the command line:

        djset add <key>=<value> [--global] [--name] [--settings]
        djset remove <key> [--global] [--name] [--settings]


Note::

    OSX and Gnome don't have an api for removing keys so on those platforms the value is cleared.


All commands trigger a django runserver reload by changing the modified time on the settings file.

An alternative/complement to storing it secretly is to export it to the current environment. The following commands (OSX & Linux only) behave the same as shell export and unset but also trigger the reload.

	dexport <key>=<value>
	dunset <key>
        