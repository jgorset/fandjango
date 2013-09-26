from django.conf import settings

# A string describing the Facebook application's ID.
FACEBOOK_APPLICATION_ID = getattr(settings, 'FACEBOOK_APPLICATION_ID')

# A string describing the Facebook application's canvas URL.
FACEBOOK_APPLICATION_CANVAS_URL = getattr(settings, 'FACEBOOK_APPLICATION_CANVAS_URL', None)

# A string describing the URL to redirect to upon authorizing users.
FACEBOOK_AUTHORIZATION_REDIRECT_URL = getattr(settings, 'FACEBOOK_AUTHORIZATION_REDIRECT_URL', None)

# A string describing the Facebook application's secret key.
FACEBOOK_APPLICATION_SECRET_KEY = getattr(settings, 'FACEBOOK_APPLICATION_SECRET_KEY')

# A string describing the Facebook application's namespace.
FACEBOOK_APPLICATION_NAMESPACE = getattr(settings, 'FACEBOOK_APPLICATION_NAMESPACE')

# A list of regular expressions describing paths on which Fandjango should be disabled.
DISABLED_PATHS = getattr(settings, 'FANDJANGO_DISABLED_PATHS', [])

# A list of regular expressions describing paths on which Fandjango should be enabled.
ENABLED_PATHS = getattr(settings, 'FANDJANGO_ENABLED_PATHS', [])

# A string describing a view that will be rendered for users that refuse to authorize the application.
AUTHORIZATION_DENIED_VIEW = getattr(settings, 'FANDJANGO_AUTHORIZATION_DENIED_VIEW', 'fandjango.views.authorization_denied')

# A list of strings describing `permissions <http://developers.facebook.com/docs/reference/api/permissions/>`_
# that will be requested upon authorizing the application.
FACEBOOK_APPLICATION_INITIAL_PERMISSIONS = getattr(settings, 'FACEBOOK_APPLICATION_INITIAL_PERMISSIONS', None)

# A string describing the Facebook's application's domain
FACEBOOK_APPLICATION_DOMAIN = getattr(settings, 'FACEBOOK_APPLICATION_DOMAIN', 'apps.facebook.com')

# A boolean describing whether to cache the signed request.
FANDJANGO_CACHE_SIGNED_REQUEST = getattr(settings, 'FACEBOOK_SIGNED_REQUEST_COOKIE', True)

# A string describing the website  URL.
FANDJANGO_SITE_URL = getattr(settings, 'FANDJANGO_SITE_URL')
