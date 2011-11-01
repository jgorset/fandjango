from datetime import datetime
from urllib import urlencode
import time

from django.conf import settings
from django.http import QueryDict
from django.core.exceptions import ImproperlyConfigured

from utils import redirect_to_facebook_authorization, parse_signed_request, get_facebook_profile, is_disabled_path, is_enabled_path
from models import Facebook, FacebookPage, User, OAuthToken
from settings import FACEBOOK_APPLICATION_CANVAS_URL, FACEBOOK_APPLICATION_SECRET_KEY, DISABLED_PATHS, ENABLED_PATHS

class FacebookMiddleware():
    """Middleware for Facebook applications."""

    def process_request(self, request):
        """Populate request.facebook."""

        if ENABLED_PATHS and DISABLED_PATHS:
            raise ImproperlyConfigured('You may configure either FANDJANGO_ENABLED_PATHS or FANDJANGO_DISABLED_PATHS, but not both.')

        if DISABLED_PATHS and is_disabled_path(request.path):
            return

        if ENABLED_PATHS and not is_enabled_path(request.path):
            return

        # Signed request found in either GET, POST or COOKIES...
        if 'signed_request' in request.REQUEST or 'signed_request' in request.COOKIES:
            request.facebook = Facebook()

            # If the request method is POST and its body only contains the signed request,
            # chances are it's a request from the Facebook platform and we'll override
            # the request method to HTTP GET to rectify their misinterpretation
            # of the HTTP protocol standard.
            #
            # References:
            # "POST for Canvas" migration at http://developers.facebook.com/docs/canvas/post/
            # "Incorrect use of the HTTP protocol" discussion at http://forum.developers.facebook.net/viewtopic.php?id=93554
            if request.method == 'POST' and 'signed_request' in request.POST:
                request.POST = QueryDict('')
                request.method = 'GET'

            request.facebook.signed_request = request.REQUEST.get('signed_request') or request.COOKIES.get('signed_request')

            parsed_signed_request = parse_signed_request(
                signed_request = request.facebook.signed_request,
                app_secret = FACEBOOK_APPLICATION_SECRET_KEY
            )

            # The application is accessed from a tab on a Facebook page...
            if 'page' in parsed_signed_request:
                request.facebook.page = FacebookPage(
                    id = parsed_signed_request['page']['id'],
                    is_admin = parsed_signed_request['page']['admin'],
                    is_liked = parsed_signed_request['page']['liked']
                )

            # User has authorized the application...
            if 'user_id' in parsed_signed_request:

                # Redirect to Facebook Authorization if the OAuth token has expired
                if parsed_signed_request.get('expires') and datetime.fromtimestamp(parsed_signed_request['expires']) < datetime.now():
                        return redirect_to_facebook_authorization(
                            redirect_uri = FACEBOOK_APPLICATION_CANVAS_URL + request.get_full_path()
                        )

                # Initialize a User object and its corresponding OAuth token
                try:
                    user = User.objects.get(facebook_id=parsed_signed_request['user_id'])
                except User.DoesNotExist:
                    oauth_token = OAuthToken.objects.create(
                        token = parsed_signed_request['oauth_token'],
                        issued_at = datetime.fromtimestamp(parsed_signed_request['issued_at']),
                        expires_at = datetime.fromtimestamp(parsed_signed_request.get('expires')) if parsed_signed_request.get('expires') else None
                    )

                    profile = get_facebook_profile(oauth_token.token)

                    user = User.objects.create(
                        facebook_id = profile.get('id'),
                        facebook_username = profile.get('username'),
                        first_name = profile.get('first_name'),
                        middle_name = profile.get('middle_name'),
                        last_name = profile.get('last_name'),
                        profile_url = profile.get('link'),
                        gender = profile.get('gender'),
                        hometown = profile['hometown'].get('name') if profile.has_key('hometown') else None,
                        location = profile['location'].get('name') if profile.has_key('location') else None,
                        bio = profile.get('bio'),
                        relationship_status = profile.get('relationship_status'),
                        political_views = profile.get('political'),
                        email = profile.get('email'),
                        website = profile.get('website'),
                        locale = profile.get('locale'),
                        verified = profile.get('verified'),
                        birthday = datetime.strptime(profile['birthday'], '%m/%d/%Y') if profile.has_key('birthday') else None,
                        timezone = profile.get('timezone'),
                        quotes = profile.get('quotes'),
                        oauth_token = oauth_token
                    )
                else:
                    user.last_seen_at = datetime.now()
                    user.authorized = True
                    if parsed_signed_request.has_key('oauth_token'):
                        user.oauth_token.token = parsed_signed_request['oauth_token']
                        user.oauth_token.issued_at = datetime.fromtimestamp(parsed_signed_request['issued_at'])
                        user.oauth_token.expires_at = datetime.fromtimestamp(parsed_signed_request['expires']) if parsed_signed_request.get('expires') else None
                        user.oauth_token.save()
                    user.save()

                request.facebook.user = user

        # ... no signed request found.
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
