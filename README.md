Djset
=====

Djset simplifies managing secrets in your django settings.

A common django configuration pattern is to use environment variables in production environments with a local unversioned settings file to hold your secret development api keys and other settings. Djset simplifies management of secret settings locally by using the shell environ, system keyring, and optionally user prompted settings.

Djset is a convenience layer on top of the python keyring library.


Installation
---------------

Djset currently requires python >= 2.6. There are currently some outstanding issues with python keyring on python 3:

    pip install djset

To install the optional environment variable helpers (in OSX or Linux) put ``source dexportunset.sh`` in your postactivate script if you use virtualenvwrapper or in your shell startup file if you don't.

Djset is entirely dependent on the DJANGO_SETTINGS_MODULE variable being set in the environment. You can use the virtualenvwrapper postactivate and postdeactivate scripts to export and unset this variable for your project or set it in the manage.py.

Add 'djset' to your project's ``INSTALLED_APPS`` setting.


Usage
--------

In your settings.py add something like the following:

    from djset import secret as s
    
    s.prompt = DEBUG
    SECRET_KEY = s.get('SECRET_KEY')  

The key is resolved in the following order:

    environment
        |
    keychain in a project settings local namespace
        |
    keychain in global namespace
        |
    prompt for input or raise ImproperlyConfigured
        
Prompt will also *add* the key to your keyring.

You can see where your key was set via a ``printsettings`` management command which enhances the builtin django command ``diffsettings`` by annotating the setting to show where your setting came from.

    $ ./manage.py printsettings

Printsettings can also show —all your active settings as per the django-extensions command of the same name.

A common practice is to set some sensible defaults for development including for example your SECRET_KEY. Djset provides for this with a twist on dict.get behaviour. 

``SECRET_KEY = s.get('SECRET_KEY', prompt_default='xyz')`` or just ``SECRET_KEY = s.get('SECRET_KEY', 'xyz')`` will set the default value the user is prompted with, but if s.prompt=False will still raise an ImproperlyConfigured error which is more useful for an automated deployment. 

By default the local namespace is your DJANGO_SETTINGS_MODULE.keyring . To use an alternate local namespace: 

    s.name = 'your.settings'

To add and remove keys use the command line:

    djsecret add <key>=<value> [--global] [--name=<name> | --settings=<settings>]
    djsecret remove <key> [--global]  [--name=<name> | --settings=<settings>]

Note:

    OSX and Gnome don't have an api for removing keys so on those platforms the value is cleared.


All commands trigger a django runserver reload by changing the modified time on the settings file.

Ordinary setting management
----------------------------

Djset has one other keyring backend for non-sensitive settings which will be stored in keyring_public.cfg at ~/.local/share/ or "$USERPROFILE/Local Settings" on Windows. Usage is identical except it wont raise an ImproperlyConfigured error by default:

    from djset import config as c
    
    tz_help = """
    Local time zone for this installation. Choices can be found here:
    http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
    """
    TIME_ZONE = c.get('TIME_ZONE', 'UTC', tz_help)

Here we’ve introduced the third optional keyword arg, *prompt_help* which presents some help when prompting the user for input. This might be useful to provide context for the setting that is required.
    
To add and remove keys use the command line:

    djconfig add <key>=<value> [--global] [--name=<name> | --settings=<settings>]
    djconfig remove <key> [--global]  [--name=<name> | --settings=<settings>]


An alternative/complement to storing settings is to export it to the current environment. The following commands (OSX & Linux only) behave the same as shell export and unset but also trigger the reload:

    dexport <key>=<value>
    dunset <key>
    
        
Customisation
--------------

Set your own keyring backend by overriding the DjSecret or DjConfig keyring attribute with your own keyring instance:

    from keyring.backends.file import PlaintextKeyring
    from djset import DjSecret
    DjSecret.keyring = PlaintextKeyring()
    s = DjSecret()

Development & Support
----------------------
Requires Nose2 for tests. Repository and issues at https://github.com/bretth/djset


        