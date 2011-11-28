from urllib import urlencode

from django.http import HttpResponse
from django.shortcuts import render

from fandjango.settings import FACEBOOK_APPLICATION_ID
from fandjango.settings import FACEBOOK_APPLICATION_CANVAS_URL
from fandjango.settings import FACEBOOK_APPLICATION_SECRET_KEY
from fandjango.settings import FACEBOOK_APPLICATION_INITIAL_PERMISSIONS
from fandjango.models import User

def authorize_application(request, redirect_uri=FACEBOOK_APPLICATION_CANVAS_URL):
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
        template_name = 'authorize_application.html',
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
        template_name = 'authorization_denied.html',
        status = 403
    )

def deauthorize_application(request):
    """
    When a user deauthorizes an application, Facebook sends a HTTP POST request to the application's
    "deauthorization callback" URL. This view picks up on requests of this sort and marks the corresponding
    users as unauthorized.
    """
    data = parse_signed_request(request.POST['signed_request'], FACEBOOK_APPLICATION_SECRET_KEY)

    user = User.objects.get(facebook_id=data['user_id'])
    user.authorized = False
    user.save()

    return HttpResponse()
