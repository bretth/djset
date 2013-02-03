Djset
=====

Djset manages your secrets in django projects using shell environment variables with fallback to your platform dependent keychain through the python keyring library. It will also trigger a reload of your local django runserver.

Installation
---------------

Djset currently requires python >= 2.6. There are currently some outstanding issues with keyring on python 3.


``pip install djset``

To install the optional environment variable helpers (in OSX or Linux) put ``source dexportunset.sh`` in your post_activate script if you use virtualenvwrapper or in your shell startup file if you don't.

Djset is entirely dependent on the DJANGO_SETTINGS_MODULE variable being set in the environment. I recommend setting it in the post_activate script like ``export DJANGO_SETTINGS_MODULE=yourproject.settings``.

Usage
--------

In your settings.py add the following against any setting you don't want to be kept in plain text:

	from djset import DjSet
	
	s = DjSet()
	KEY = s.get('KEY')

The key is resolved in the following order:

	environment
	    |
	keychain in the *KEY.NAME.keyring* namespace (local)
	    |
	keychain in the *KEY.keyring* namespace (global)

By default the *NAME* in the namespace is your DJANGO_SETTINGS_MODULE. To use an alternate namespace: 

	s = DjSet(name='yourname')
        
To set a default value if the key is absent from all locations:
``SECRET_KEY = s.get('SECRET_KEY', 'xyz’)``

Lets say you introduce a new setting into a shared repository but want to let developers set their own values. To prompt for the value instead of raising an error:

``s.prompt = True``

To add and remove keys use the command line:

        djset add <key>=<value> [--global] [--name]
        djset remove <key> [--global] [--name]

For example ``djset add SECRET_KEY=xyz``

Note::

    OSX and Gnome don't have an api for removing keys so on those platforms the value is cleared.


All commands trigger a django runserver reload by changing the modified time on the settings file.

An alternative/complement to storing it secretly is to export it to the current environment. The following commands (OSX & Linux only) behave the same as shell export and unset but also trigger the reload. ie:

	dexport <key>=<value>
	dunset <key>


