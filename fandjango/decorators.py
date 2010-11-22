from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings

from utils import redirect_to_facebook_authorization

def facebook_authorization_required(function):
  """Redirect Facebook canvas views to authorization if required."""
  def wrapper(request, *args, **kwargs):
    if not request.facebook:
      return redirect_to_facebook_authorization(
        redirect_uri = settings.FACEBOOK_APPLICATION_URL + request.get_full_path()
      )
    return function(request, *args, **kwargs)
  return wrapper