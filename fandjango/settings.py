from warnings import warn

from django.conf import settings

# A string describing the Facebook application's ID.
FACEBOOK_APPLICATION_ID = getattr(settings, 'FACEBOOK_APPLICATION_ID')

# A string describing the Facebook application's secret key.
FACEBOOK_APPLICATION_SECRET_KEY = getattr(settings, 'FACEBOOK_APPLICATION_SECRET_KEY')

# A string describing the Facebook application's canvas URL.
try:
    FACEBOOK_APPLICATION_CANVAS_URL = getattr(settings, 'FACEBOOK_APPLICATION_CANVAS_URL')
except AttributeError:
    FACEBOOK_APPLICATION_CANVAS_URL = getattr(settings, 'FACEBOOK_APPLICATION_URL')
    warn('FACEBOOK_APPLICATION_URL is deprecated. Please use FACEBOOK_APPLICATION_CANVAS_URL instead.', DeprecationWarning)

# A list of regular expressions describing paths on which Fandjango should be disabled.
DISABLED_PATHS = getattr(settings, 'FANDJANGO_DISABLED_PATHS', [])

# A list of regular expressions describing paths on which Fandjango should be enabled.
ENABLED_PATHS = getattr(settings, 'FANDJANGO_ENABLED_PATHS', [])

# A string describing a view that will be rendered for users that refuse to authorize the application.
AUTHORIZATION_DENIED_VIEW = getattr(settings, 'FANDJANGO_AUTHORIZATION_DENIED_VIEW', 'fandjango.views.authorization_denied')

# A list of strings describing `permissions <http://developers.facebook.com/docs/reference/api/permissions/>`_ that will be
# requested upon authorizing the application.
FACEBOOK_APPLICATION_INITIAL_PERMISSIONS = getattr(settings, 'FACEBOOK_APPLICATION_INITIAL_PERMISSIONS', None)
