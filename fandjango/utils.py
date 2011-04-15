from urllib import urlencode
import base64
import re
import hmac
import hashlib
from httplib import HTTPSConnection

try:
   import json
except ImportError:
   from django.utils import simplejson as json

from django.http import HttpResponse
from django.conf import settings

from settings import IGNORE_PATHS

def redirect_to_facebook_authorization(redirect_uri):
    """
    Redirect the user to authorize the application.
    
    Redirection is done by rendering a JavaScript snippet that redirects the parent
    window to the authorization URI, since Facebook will not allow this inside an iframe.
    """
    request_variables = {
        'client_id': settings.FACEBOOK_APPLICATION_ID,
        'redirect_uri': redirect_uri
    }
    
    if hasattr(settings, 'FACEBOOK_APPLICATION_INITIAL_PERMISSIONS'):
        request_variables['scope'] = ', '.join(settings.FACEBOOK_APPLICATION_INITIAL_PERMISSIONS)
    
    urlencoded_request_variables = urlencode(request_variables)
    
    html = """
        <!DOCTYPE html>
        
        <html>
        
            <head>
                <script type="text/javascript">
                    window.parent.location = "https://graph.facebook.com/oauth/authorize?%s";
                </script>
            </head>
            
            <body>
                <noscript>
                    You must <a href="https://graph.facebook.com/oauth/authorize?%s">authorize the application</a> in order to continue.
                </noscript>
            </body>
        
        </html>
    """ % (urlencoded_request_variables, urlencoded_request_variables)
    
    return HttpResponse(html)
    
def parse_signed_request(signed_request, app_secret):
        """Return dictionary with signed request data."""
        try:
            l = signed_request.split('.', 2)
            encoded_sig = str(l[0])
            payload = str(l[1])
        except IndexError:
            raise ValueError("Signed request malformed")
        
        sig = base64.urlsafe_b64decode(encoded_sig + "=" * ((4 - len(encoded_sig) % 4) % 4))
        data = base64.urlsafe_b64decode(payload + "=" * ((4 - len(payload) % 4) % 4))

        data = json.loads(data)

        if data.get('algorithm').upper() != 'HMAC-SHA256':
            raise ValueError("Signed request is using an unknown algorithm")
        else:
            expected_sig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()

        if sig != expected_sig:
            raise ValueError("Signed request signature mismatch")
        else:
            return data
            
def get_facebook_profile(oauth_token):
    """
    Query Facebook's Graph API for the current user's profile and
    parse it into a dictionary.
    
    Arguments:
    oauth_token -- A string describing the user's OAuth token.
    """
    connection = HTTPSConnection('graph.facebook.com')
    connection.request('GET', 'me?access_token=%s' % oauth_token)
    
    return json.loads(connection.getresponse().read())
    
def is_ignored_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the IGNORE_PATHS setting.
    
    Arguments:
    path -- A string describing the path to be matched.
    """
    for ignore_path in IGNORE_PATHS:
        match = re.search(ignore_path, path[1:])
        if match:
            return True
    return False