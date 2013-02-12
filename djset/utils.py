import os


def getbool(key, default=False):
    """
    Returns True or False for any TRUE, FALSE, 0, or 1.
    Other values return default.
    """
    value = os.getenv(key)
    if value and value.lower() in ('true', '1'):
        value = True
    elif value and value.lower() in ('false', '0'):
        value = False
    else:
        value = default
    return value


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