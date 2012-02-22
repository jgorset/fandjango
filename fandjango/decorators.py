from functools import wraps

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.handlers.wsgi import WSGIRequest

from fandjango.utils import get_post_authorization_redirect_url
from fandjango.views import authorize_application
from fandjango.settings import FACEBOOK_APPLICATION_DOMAIN, FACEBOOK_APPLICATION_NAMESPACE
from fandjango.utils import get_post_authorization_redirect_url

def facebook_authorization_required(redirect_uri=None):
    """
    Require the user to authorize the application.

    :param redirect_uri: A string describing an URI to redirect to after authorization is complete.
                         Defaults to the current URI in the Facebook canvas (e.g.
                         ``http://apps.facebook.com/myapp/current/path``).
    """

    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):

            if not request.facebook or not request.facebook.user:
                return authorize_application(
                    request = request,
                    redirect_uri = get_post_authorization_redirect_url(request)
                )

            return function(request, *args, **kwargs)
        return wrapper

    if callable(redirect_uri):
        function = redirect_uri
        redirect_uri = None

        return decorator(function)
    else:
        return decorator
