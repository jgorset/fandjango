from datetime import datetime
from urllib import urlencode
import time
import re

from django.conf import settings

from utils import redirect_to_facebook_authorization, parse_signed_request, get_facebook_profile
from models import Facebook, FacebookPage, User, OAuthToken
from settings import FACEBOOK_APPLICATION_URL, FACEBOOK_APPLICATION_SECRET_KEY

class FacebookMiddleware():
    """Middleware for Facebook applications."""
    
    def process_request(self, request):
        """Populate request.facebook."""
        
        # Signed request found in either GET, POST or COOKIES...
        if 'signed_request' in request.REQUEST or 'signed_request' in request.COOKIES:
            request.facebook = Facebook()
            
            request.facebook.signed_request = request.REQUEST.get('signed_request') or request.COOKIES.get('signed_request')
            
            facebook_data = parse_signed_request(
                signed_request = request.facebook.signed_request,
                app_secret = FACEBOOK_APPLICATION_SECRET_KEY
            )
            
            # The application is accessed from a tab on a Facebook page...
            if 'page' in facebook_data:
                request.facebook.page = FacebookPage(
                    id = facebook_data['page']['id'],
                    is_admin = facebook_data['page']['admin'],
                    is_liked = facebook_data['page']['liked']
                )
            
            # User has authorized the application...
            if 'user_id' in facebook_data:
                
                # Redirect to Facebook Authorization if the OAuth token has expired
                if facebook_data['expires']:
                    if datetime.fromtimestamp(facebook_data['expires']) < datetime.now():
                        return redirect_to_facebook_authorization(
                            redirect_uri = FACEBOOK_APPLICATION_URL + request.get_full_path()
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
                    
                    profile = get_facebook_profile(oauth_token.token)
                    
                    user = User.objects.create(
                        facebook_id = profile.get('id'),
                        first_name = profile.get('first_name'),
                        last_name = profile.get('last_name'),
                        profile_url = profile.get('link'),
                        gender = profile.get('gender'),
                        oauth_token = oauth_token
                    )
                else:
                    user.last_seen_at = datetime.now()
                    user.save()
                    
                    user.oauth_token.token = facebook_data['oauth_token']
                    user.oauth_token.issued_at = datetime.fromtimestamp(facebook_data['issued_at'])
                    user.oauth_token.expires_at = datetime.fromtimestamp(facebook_data['expires']) if facebook_data['expires'] else None
                    user.oauth_token.save()
                
                request.facebook.user = user
                
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
