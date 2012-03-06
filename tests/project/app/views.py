from django.http import HttpResponse

from fandjango.decorators import facebook_authorization_required

@facebook_authorization_required
def home(request):
    return HttpResponse()

@facebook_authorization_required(permissions=["checkins"])
def places(request):
    return HttpResponse()

@facebook_authorization_required(redirect_uri="http://example.org")
def redirect(request):
  return HttpResponse()
