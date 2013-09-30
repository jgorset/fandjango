import re
from datetime import timedelta
from urlparse import urlparse
from functools import wraps

from django.core.cache import cache
from django.utils.importlib import import_module

from fandjango.settings import FACEBOOK_APPLICATION_CANVAS_URL
from fandjango.settings import FACEBOOK_APPLICATION_DOMAIN
from fandjango.settings import FACEBOOK_APPLICATION_NAMESPACE
from fandjango.settings import DISABLED_PATHS
from fandjango.settings import ENABLED_PATHS
from fandjango.settings import AUTHORIZATION_DENIED_VIEW
from fandjango.settings import FANDJANGO_SITE_URL

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

def authorization_denied_view(request):
    """Proxy for the view referenced in ``FANDJANGO_AUTHORIZATION_DENIED_VIEW``."""
    authorization_denied_module_name = AUTHORIZATION_DENIED_VIEW.rsplit('.', 1)[0]
    authorization_denied_view_name = AUTHORIZATION_DENIED_VIEW.split('.')[-1]

    authorization_denied_module = import_module(authorization_denied_module_name)
    authorization_denied_view = getattr(authorization_denied_module, authorization_denied_view_name)

    return authorization_denied_view(request)

def get_post_authorization_redirect_url(request, canvas=True):
    """Determine the URL users should be redirected to upon authorization the application."""

    path = request.get_full_path()

    if canvas:
        if FACEBOOK_APPLICATION_CANVAS_URL:
            path = path.replace(urlparse(FACEBOOK_APPLICATION_CANVAS_URL).path, '')

        redirect_uri = 'http://%(domain)s/%(namespace)s%(path)s' % {
            'domain': FACEBOOK_APPLICATION_DOMAIN,
            'namespace': FACEBOOK_APPLICATION_NAMESPACE,
            'path': path
        }
    else:
        path = path.replace(urlparse(FANDJANGO_SITE_URL).path, '')
        redirect_uri = FANDJANGO_SITE_URL + path

    return redirect_uri

def get_full_path(request, remove_querystrings=[]):
    path = request.get_full_path()
    for qs in remove_querystrings:
        path = re.sub(r'&?' + qs + '=?(.+)?&?', '', path)
    return path
