from functools import wraps

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.handlers.wsgi import WSGIRequest
from django.conf import settings

from utils import redirect_to_facebook_authorization

def facebook_authorization_required(redirect_uri=False, app_data=''):
    """
    Redirect Facebook canvas views to authorization if required.
    
    Arguments:
    redirect_uri -- A string describing an URI to redirect to after authorization is complete.
                    Defaults to current URI in Facebook canvas (ex. http://apps.facebook.com/myapp/path/).
    """
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            
            request = [arg for arg in args if arg.__class__ is WSGIRequest][0]
            
            page_tab = None
            if not request.facebook or not request.facebook.user:
                page_tab = request.facebook.page.url + "?sk=app_%s&app_data=%s" % (settings.FACEBOOK_APPLICATION_ID, request.get_full_path())

                return redirect_to_facebook_authorization(
                        redirect_uri = redirect_uri or page_tab or settings.FACEBOOK_APPLICATION_URL + request.get_full_path()
                    
            return function(*args, **kwargs)
        return wrapper
    return decorator




                                                                                                                                            )   


