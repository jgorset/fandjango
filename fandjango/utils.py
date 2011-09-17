from urllib import urlencode
import base64
import re
import hmac
import hashlib
from httplib import HTTPSConnection
from fandjango.settings import FACEBOOK_APPLICATION_SECRET_KEY

try:
   import json
except ImportError:
   from django.utils import simplejson as json

from django.http import HttpResponse
from django.conf import settings

from settings import DISABLED_PATHS, ENABLED_PATHS

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

def create_signed_request(*args, **kwargs):
    """
    Returns a string that is a valid signed_request parameter specified by Facebook
    see: http://developers.facebook.com/docs/authentication/signed_request/
    
    Arguments:
    args -- optional An integer representing the facebook uid of a user. If this argument is given
                a default JSON object will be used for the request that is signed. The JSON object
                will contain the following fields and values:
                    - 'user_id': args[0]
                    - 'algorithm': 'HMAC-SHA256'
                    - 'expires': 0
                    - 'oauth_token': '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
                    - 'issued_at': 1306179904
    kwargs -- optional A Dict which will be used as the JSON object for the request that is signed. The Dict must contain
                the following fields:
                    - 'user_id' for which the value must be an integer representing the Facebook uid of a user
                    - 'algorithm' which must be set to the value 'HMAC-SHA256'
                other optional fields:
                    - 'issued_at'
                    - 'oauth_token'
                    - 'expires'
                    - 'app_data'
                    - 'page'
                    - 'profile_id'

    Examples:
        create_signed_request(199)
        create_signed_request({'user_id': 199, 'algorithm': 'HMAC-SHA256'})

    Note: if no arguments are given, a default signed_request String will returned which be semantically be the same as calling
    create_signed_request(1)
    """
    payload = {'user_id': 1, 'algorithm': 'HMAC-SHA256', 'expires': 0, 'oauth_token': '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk', 'issued_at': 1306179904}
    if args is not None:
        payload['user_id'] = args[0]
    elif kwargs is not None:
        payload = kwargs

    return __create_signed_request_parameter(json.dumps(payload))

def __prepend_signature(payload):
        """
            Returns a SHA256 signed and base64 encoded signature based on the given payload

            Arguments:
            payload - a base64url encoded String
        """
        dig = hmac.new(FACEBOOK_APPLICATION_SECRET_KEY, msg=payload, digestmod=hashlib.sha256).digest()
        dig = base64.urlsafe_b64encode(dig)
        return dig

def __create_signed_request_parameter(payload):
        """
            Returns a String value usable as the Facebook signed_request parameter. The String will be based on the given payload.
            The signed_request parameter is the concatenation of a HMAC SHA-256 signature string, a period (.), and a
            the base64url encoded payload.

            Arguments:
            payload - a JSON formatted String
        """
        base64_encoded_payload = base64.urlsafe_b64encode(payload)
        return __prepend_signature(base64_encoded_payload) + "." + base64_encoded_payload
            
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
    
def is_disabled_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the DISABLED_PATHS setting.
    
    Arguments:
    path -- A string describing the path to be matched.
    """
    for disabled_path in DISABLED_PATHS:
        match = re.search(disabled_path, path[1:])
        if match:
            return True
    return False
    
def is_enabled_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the ENABLED_PATHS setting.
    
    Arguments:
    path -- A string describing the path to be matched.
    """
    for enabled_path in ENABLED_PATHS:
        match = re.search(enabled_path, path[1:])
        if match:
            return True
    return False