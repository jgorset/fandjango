from urllib import urlencode

from django.http import HttpResponse
from django.shortcuts import render

from facepy import SignedRequest

from fandjango.models import User
from fandjango.settings import (
    FACEBOOK_APPLICATION_ID, FACEBOOK_APPLICATION_DOMAIN,
    FACEBOOK_APPLICATION_NAMESPACE, FACEBOOK_APPLICATION_SECRET_KEY,
    FACEBOOK_APPLICATION_INITIAL_PERMISSIONS
)

def authorize_application(request, redirect_uri='https://%s/%s' % (FACEBOOK_APPLICATION_DOMAIN, FACEBOOK_APPLICATION_NAMESPACE)):
    """
    Redirect the user to authorize the application.

    Redirection is done by rendering a JavaScript snippet that redirects the parent
    window to the authorization URI, since Facebook will not allow this inside an iframe.
    """
    query = {
        'client_id': FACEBOOK_APPLICATION_ID,
        'redirect_uri': redirect_uri
    }

    if FACEBOOK_APPLICATION_INITIAL_PERMISSIONS:
        query['scope'] = ', '.join(FACEBOOK_APPLICATION_INITIAL_PERMISSIONS)

    return render(
        request = request,
        template_name = 'fandjango/authorize_application.html',
        dictionary = {
            'url': 'https://graph.facebook.com/oauth/authorize?%s' % urlencode(query)
        },
        status = 303
    )

def authorization_denied(request):
    """
    Render a template for users that refuse to authorize the application.
    """
    return render(
        request = request,
        template_name = 'fandjango/authorization_denied.html',
        status = 403
    )

def deauthorize_application(request):
    """
    When a user deauthorizes an application, Facebook sends a HTTP POST request to the application's
    "deauthorization callback" URL. This view picks up on requests of this sort and marks the corresponding
    users as unauthorized.
    """
    if request.facebook:
        user = User.objects.get(
            facebook_id = request.facebook.signed_request.user.id
        )

        user.authorized = False
        user.save()

        return HttpResponse()
    else:
        return HttpResponse(status=400)
