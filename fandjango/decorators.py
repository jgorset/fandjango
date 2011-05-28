from functools import wraps

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings

from utils import redirect_to_facebook_authorization

def facebook_authorization_required(redirect_uri=False):
    """
    Redirect Facebook canvas views to authorization if required.

    Arguments:
    redirect_uri -- A string describing an URI to redirect to after authorization is complete.
                    Defaults to current URI in Facebook canvas (ex. http://apps.facebook.com/myapp/path/).
    """
    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if not request.facebook or not request.facebook.user:
                    return redirect_to_facebook_authorization(
                        redirect_uri = redirect_uri or settings.FACEBOOK_APPLICATION_URL + request.get_full_path()
                    )
            return function(request, *args, **kwargs)
        return wrapper
    return decorator(redirect_uri)
