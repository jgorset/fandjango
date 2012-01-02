import re
from datetime import timedelta
from functools import wraps

from django.core.cache import cache

from fandjango.settings import DISABLED_PATHS
from fandjango.settings import ENABLED_PATHS

def is_disabled_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the DISABLED_PATHS setting.

    :param path: A string describing the path to be matched.
    """
    for disabled_path in DISABLED_PATHS:
        match = re.search(disabled_path, path[1:])
        if match:
            return True
    return False

def is_enabled_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the ENABLED_PATHS setting.

    :param path: A string describing the path to be matched.
    """
    for enabled_path in ENABLED_PATHS:
        match = re.search(enabled_path, path[1:])
        if match:
            return True
    return False

def cached_property(**kwargs):
    """Cache the return value of a property."""
    def decorator(function):
        @wraps(function)
        def wrapper(self):
            key = 'fandjango.%(model)s.%(property)s_%(pk)s' % {
                'model': self.__class__.__name__,
                'pk': self.pk,
                'property': function.__name__
            }

            cached_value = cache.get(key)

            delta = timedelta(**kwargs)

            if cached_value is None:
                value = function(self)
                cache.set(key, value, delta.days * 86400 + delta.seconds)
            else:
                value = cached_value

            return value
        return wrapper
    return decorator
