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