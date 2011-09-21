from datetime import datetime
from urllib import urlencode
import base64
import re
import hmac
import hashlib
from httplib import HTTPSConnection
from fandjango.settings import FACEBOOK_APPLICATION_SECRET_KEY
import time

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

def create_signed_request(app_secret, user_id=1, issued_at=None, oauth_token=None, expires=None, app_data=None, page=None):
    """
    Returns a string that is a valid signed_request parameter specified by Facebook
    see: http://developers.facebook.com/docs/authentication/signed_request/
    
    Arguments:
    app_secret -- the secret key that Facebook assigns to each Facebook application
    user_id -- optional a long representing the Facebook user identifier (UID) of a user
    issued_at -- optional an int or a datetime representing a timestamp when the request was signed
    oauth_token -- optional a String token to pass in to the Facebook graph api
    expires -- optional an int or a datetime representing a timestamp at which the oauth token expires
    app_data -- optional a dict containing additional application data
    page -- optional a dict having the keys id (string), liked (boolean) if the user has liked the page and optionally admin (boolean) if the user is an admin of that page.

    Regardless of which arguments are given, the encoded JSON object will always contain the following properties:
        -- user_id
        -- algorithm
        -- issued_at

    Examples:
        create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY)
        create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, user_id=199)
        create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, user_id=199, issued_at=1254459600)

    """
    payload = {'user_id': user_id, 'algorithm': 'HMAC-SHA256'}

    value = int(time.time())
    if issued_at is not None and (isinstance(issued_at, datetime) or isinstance(issued_at, int)):
        value = issued_at
        if isinstance(issued_at, datetime):
            value = int(time.mktime(issued_at.timetuple()))
    payload['issued_at'] = value

    if oauth_token is not None:
        payload['oauth_token'] = oauth_token
    if expires is not None and (isinstance(expires, datetime) or isinstance(expires, int)):
        value = expires
        if isinstance(expires, datetime):
            value = int(time.mktime(expires.timetuple()))
        payload['expires'] = value
    if app_data is not None and isinstance(app_data, dict):
        payload['app_data'] = app_data
    if page is not None and isinstance(page, dict):
        payload['page'] = page

    return __create_signed_request_parameter(app_secret, json.dumps(payload))

def __prepend_signature(app_secret, payload):
        """
            Returns a SHA256 signed and base64 encoded signature based on the given payload

            Arguments:
            app_secret -- the secret key that Facebook assigns to each Facebook application
            payload -- a base64url encoded String
        """
        dig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()
        dig = base64.urlsafe_b64encode(dig)
        return dig

def __create_signed_request_parameter(app_secret, payload):
        """
            Returns a String value usable as the Facebook signed_request parameter. The String will be based on the given payload.
            The signed_request parameter is the concatenation of a HMAC SHA-256 signature string, a period (.), and a
            the base64url encoded payload.

            Arguments:
            app_secret -- the secret key that Facebook assigns to each Facebook application
            payload -- a JSON formatted String
        """
        base64_encoded_payload = base64.urlsafe_b64encode(payload)
        return __prepend_signature(app_secret, base64_encoded_payload) + "." + base64_encoded_payload
            
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