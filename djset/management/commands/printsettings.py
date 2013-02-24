"""
printsettings
==============

Replacement diffsettings which also shows the source of djset managed settings.
Also optionally shows all active settings. 

Derived in part from django diffsettings management command.
Copyright (c) Django Software Foundation and individual contributors.
All rights reserved.
https://raw.github.com/django/django/master/LICENSE
"""


from django.core.management.base import NoArgsCommand
from optparse import make_option

def module_to_dict(module, omittable=lambda k: k.startswith('_')):
    "Converts a module namespace to a Python dictionary. Used by get_settings_diff."
    return dict([(k, repr(v)) for k, v in module.__dict__.items() if not omittable(k)])



class Command(NoArgsCommand):
    help = """Displays differences between the current settings.py and Django's
    default settings. Settings that don't appear in the defaults are
    followed by "###". Djset settings are followed by "# "
    and the source of the setting in brackets ( )
    """

    requires_model_validation = False
    
    option_list = NoArgsCommand.option_list + (
        make_option('--all', action='store_false', dest='all',
                    help='Print all active settings.'),
    )
    
    def handle_noargs(self, **options):
        # Inspired by Postfix's "postconf -n".
        from django.conf import settings, global_settings
        from djset import secret, config
                
        # Because settings are imported lazily, we need to explicitly load them.
        settings._setup()

        user_settings = module_to_dict(settings._wrapped)
        default_settings = module_to_dict(global_settings)
        
        output = []
        nb = False
        note_key = []
        all_settings = options.get('all')
        for key in sorted(user_settings.keys()):
            line = []
            value = user_settings[key]
            if key not in default_settings:
                line.append("%s = %s  ### " % (key, value))
            elif all_settings or (user_settings[key] != default_settings[key]):
                line.append("%s = %s " % (key, value))
            # Annotate the values with the djset source
            if key in secret.kns:
                line.append("# (%s) " % secret.kns.get(key))
            if key in config.kns:
                line.append("# (%s) " % config.kns.get(key))
            if key in secret.kns and key in config.kns:
                line.append('***')
                note_key.append(key)
                nb = True
            if line:
                output.append(''.join(line))
        if nb:
            output.append(
            "*** Designates setting(s) '%s' set by both Djset config and secret. " \
            "The actual source will depend on the order they were evaluated." % ', '.join(note_key)
            )
            
        return '\n'.join(output)
        
