from datetime import datetime
from urllib import urlencode
import base64
import hmac
import hashlib
import json
import time

import facebook

from django.conf import settings

from utils import redirect_to_facebook_authorization
from models import User, OAuthToken

class FacebookMiddleware():
    """
    Middleware for Facebook applications.
    
    FacebookMiddleware populates the request object with data for the current facebook user (see
    the process_request method for specifics).
    """
    
    def process_request(self, request):
        """Populate request.facebook_user with information about the current user (see models.User for details)."""
        if 'signed_request' in request.REQUEST or 'signed_request' in request.COOKIES:
            facebook_data = parse_signed_request(
                signed_request = request.REQUEST['signed_request'] if 'signed_request' in request.REQUEST else request.COOKIES['signed_request'],
                app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
            )
            
            # User is authenticated...
            if 'user_id' in facebook_data:
                
                # Redirect to Facebook Authorization if the OAuth token has expired
                if facebook_data['expires']:
                    if datetime.fromtimestamp(facebook_data['expires']) < datetime.now():
                        return redirect_to_facebook_authorization(
                            redirect_uri = settings.FACEBOOK_APPLICATION_URL + request.get_full_path()
                        )
                
                # Initialize a User object and its corresponding OAuth token
                try:
                    user = User.objects.get(facebook_id=facebook_data['user_id'])
                except User.DoesNotExist:
                    oauth_token = OAuthToken.objects.create(
                        token = facebook_data['oauth_token'],
                        issued_at = datetime.fromtimestamp(facebook_data['issued_at']),
                        expires_at = datetime.fromtimestamp(facebook_data['expires'])
                    )
                    
                    profile = facebook.GraphAPI(oauth_token.token).get_object('me')
                    
                    user = User.objects.create(
                        facebook_id = profile['id'],
                        first_name = profile['first_name'],
                        last_name = profile['last_name'],
                        profile_url = profile['link'],
                        gender = profile['gender'],
                        oauth_token = oauth_token
                    )
                else:
                    user.oauth_token.token = facebook_data['oauth_token']
                    user.oauth_token.issued_at = datetime.fromtimestamp(facebook_data['issued_at'])
                    user.oauth_token.expires_at = datetime.fromtimestamp(facebook_data['expires'])
                
                request.facebook_user = user
            
            # User is not authenticated...
            else:
                request.facebook = False
        # No signed request found
        else:
            request.facebook = False


    def process_response(self, request, response):
        """
        Set compact P3P policies and save signed request to cookie.
        
        P3P is a WC3 standard (see http://www.w3.org/TR/P3P/), and although largely ignored by most
        browsers it is considered by IE before accepting third-party cookies (ie. cookies set by
        documents in iframes). If they are not set correctly, IE will not set these cookies.
        
        """
        if 'signed_request' in request.REQUEST:
            response.set_cookie('signed_request', request.REQUEST['signed_request'])
        response['P3P'] = 'CP="IDC CURa ADMa OUR IND PHY ONL COM STA"'
        return response

    
    
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
