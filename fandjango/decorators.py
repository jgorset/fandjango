from functools import wraps

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.handlers.wsgi import WSGIRequest

from fandjango.utils import get_post_authorization_redirect_url
from fandjango.views import authorize_application
from fandjango.settings import FACEBOOK_APPLICATION_DOMAIN
from fandjango.settings import FACEBOOK_APPLICATION_NAMESPACE
from fandjango.settings import FACEBOOK_APPLICATION_INITIAL_PERMISSIONS
from fandjango.utils import get_post_authorization_redirect_url

def facebook_authorization_required(redirect_uri=None, permissions=None):
    """
    Require the user to authorize the application.

    :param redirect_uri: A string describing an URI to redirect to after authorization is complete.
                         Defaults to the current URI in the Facebook canvas (e.g.
                         ``http://apps.facebook.com/myapp/current/path``).
    :param permissions: A list of strings describing Facebook permissions.
    """

    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):

            # The user has already authorized the application, but the given view requires
            # permissions besides the defaults listed in ``FACEBOOK_APPLICATION_DEFAULT_PERMISSIONS``.
            #
            # Derive a list of outstanding permissions and prompt the user to grant them.
            if request.facebook and request.facebook.user and permissions:
                outstanding_permissions = [p for p in permissions if p not in request.facebook.user.permissions]

                if outstanding_permissions:
                    return authorize_application(
                        request = request,
                        redirect_uri = redirect_uri or get_post_authorization_redirect_url(request),
                        permissions = outstanding_permissions
                    )

            # The user has not authorized the application yet.
            #
            # Concatenate the default permissions with permissions required for this particular view.
            if not request.facebook or not request.facebook.user:
                return authorize_application(
                    request = request,
                    redirect_uri = redirect_uri or get_post_authorization_redirect_url(request),
                    permissions = (FACEBOOK_APPLICATION_INITIAL_PERMISSIONS or []) + (permissions or [])
                )

            return function(request, *args, **kwargs)
        return wrapper

    if callable(redirect_uri):
        function = redirect_uri
        redirect_uri = None

        return decorator(function)
    else:
        return decorator
