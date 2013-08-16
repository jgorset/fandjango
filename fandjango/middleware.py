from datetime import timedelta
from urlparse import parse_qs

from django.http import QueryDict
from django.core.exceptions import ImproperlyConfigured

from fandjango.views import authorize_application
from fandjango.models import Facebook, User, OAuthToken
from fandjango.settings import (
    FACEBOOK_APPLICATION_SECRET_KEY, FACEBOOK_APPLICATION_ID,
    FANDJANGO_CACHE_SIGNED_REQUEST, DISABLED_PATHS, ENABLED_PATHS
)
from fandjango.utils import (
    is_disabled_path, is_enabled_path,
    authorization_denied_view, get_post_authorization_redirect_url
)

from facepy import SignedRequest, GraphAPI

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    def now():
        return datetime.now()

from dateutil.tz import tzlocal

class BaseMiddleware():

    def is_valid_path(self, request):
        if ENABLED_PATHS and DISABLED_PATHS:
            raise ImproperlyConfigured(
                'You may configure either FANDJANGO_ENABLED_PATHS '
                'or FANDJANGO_DISABLED_PATHS, but not both.'
            )

        if DISABLED_PATHS and is_disabled_path(request.path):
            return

        if ENABLED_PATHS and not is_enabled_path(request.path):
            return

        return True

class FacebookMiddleware(BaseMiddleware):
    """Middleware for Facebook auth on websites."""

    def process_request(self, request):
        """Process the signed request."""

        if not self.is_valid_path(request):
            return

        if hasattr(request, "facebook") and request.facebook:
            return

        # An error occured during authorization...
        if 'error' in request.GET:
            # The user refused to authorize the application...
            if request.GET['error'] == 'access_denied':
                return authorization_denied_view(request)

        request.facebook = Facebook()
        oauth_token = False

        # Is there a token in the current session already present?
        if 'oauth_token' in request.session:
            try:
                # Check if the current token is already in DB
                oauth_token = OAuthToken.objects.get(token=request.session['oauth_token'])
            except OAuthToken.DoesNotExist:
                # It's in the session but it's not in the DB, weird, better delete it and get new one..
                del request.session['oauth_token']
                request.facebook = False
                return

        # Is there a code in the GET request?
        elif 'code' in request.GET:
            graph = GraphAPI()

            # Exchange code for an access_token
            response = graph.get('oauth/access_token',
                client_id = FACEBOOK_APPLICATION_ID,
                redirect_uri = get_post_authorization_redirect_url(request, canvas=False),
                client_secret = FACEBOOK_APPLICATION_SECRET_KEY,
                code = request.GET['code'],
            )
    
            components = parse_qs(response)
            
            # Save new OAuth-token in DB
            oauth_token = OAuthToken.objects.create(
                token = components['access_token'][0],
                issued_at = now(),
                expires_at = now() + timedelta(seconds = int(components['expires'][0]))
            )
        
        # There is a valid access_token
        if oauth_token:
            # Redirect to Facebook authorization if the OAuth token has expired
            if oauth_token.expired:
                request.facebook = False
                return

            # Is there a user already connected to the current token?
            try:
                user = oauth_token.user
                # Update user's details
                user.last_seen_at = now()
                user.authorized = True
                user.save()
            except User.DoesNotExist:
                g = GraphAPI(oauth_token.token)
                profile = g.get('me')
                
                # Either the user already exists and its just a new token, or user and token both are new
                try:
                    user = User.objects.get(facebook_id = profile.get('id'))
                except User.DoesNotExist:
                    # Create a new user to go with token
                    user = User.objects.create(
                        facebook_id = profile.get('id'),
                        oauth_token = oauth_token
                    )                    
                
                user.synchronize(profile)
                
                # Delete old access token if there is any and  only if the new one is different
                if user.oauth_token != oauth_token:
                    user.oauth_token.delete()
                
                user.oauth_token = oauth_token
                user.save()

            if not user.oauth_token.extended:
                # Attempt to extend the OAuth token, but ignore exceptions raised by
                # bug #102727766518358 in the Facebook Platform.
                #
                # http://developers.facebook.com/bugs/102727766518358/
                try:
                    user.oauth_token.extend()
                except:
                    pass

            request.facebook.user = user
            request.session['oauth_token'] = user.oauth_token.token

    def process_response(self, request, response):
        """
        Set compact P3P policies and save signed request to cookie.

        P3P is a WC3 standard (see http://www.w3.org/TR/P3P/), and although largely ignored by most
        browsers it is considered by IE before accepting third-party cookies (ie. cookies set by
        documents in iframes). If they are not set correctly, IE will not set these cookies.
        """
        if 'oauth_token' in request.session:
            response['P3P'] = 'CP="IDC CURa ADMa OUR IND PHY ONL COM STA"'
        return response

class FacebookCanvasMiddleware(BaseMiddleware):
    """Middleware for Facebook canvas applications."""

    def process_request(self, request):
        """Process the signed request."""

        if not self.is_valid_path(request):
            return

        if hasattr(request, "facebook") and request.facebook:
            return

        # An error occured during authorization...
        if 'error' in request.GET:
            # The user refused to authorize the application...
            if request.GET['error'] == 'access_denied':
                return authorization_denied_view(request)

        # Signed request found in either GET, POST or COOKIES...
        if 'signed_request' in request.REQUEST or 'signed_request' in request.COOKIES:
            request.facebook = Facebook()

            # If the request method is POST and its body only contains the signed request,
            # chances are it's a request from the Facebook platform and we'll override
            # the request method to HTTP GET to rectify their misinterpretation
            # of the HTTP standard.
            #
            # References:
            # "POST for Canvas" migration at http://developers.facebook.com/docs/canvas/post/
            # "Incorrect use of the HTTP protocol" discussion at http://forum.developers.facebook.net/viewtopic.php?id=93554
            if request.method == 'POST' and 'signed_request' in request.POST:
                request.POST = QueryDict('')
                request.method = 'GET'

            try:
                request.facebook.signed_request = SignedRequest(
                    signed_request = request.REQUEST.get('signed_request') or request.COOKIES.get('signed_request'),
                    application_secret_key = FACEBOOK_APPLICATION_SECRET_KEY
                )
            except SignedRequest.Error:
                request.facebook = False

            # Valid signed request and user has authorized the application
            if request.facebook and request.facebook.signed_request.user.has_authorized_application:

                # Redirect to Facebook Authorization if the OAuth token has expired
                if request.facebook.signed_request.user.oauth_token.has_expired:
                    return authorize_application(
                        request = request,
                        redirect_uri = get_post_authorization_redirect_url(request)
                    )

                # Initialize a User object and its corresponding OAuth token
                try:
                    user = User.objects.get(facebook_id=request.facebook.signed_request.user.id)
                except User.DoesNotExist:
                    oauth_token = OAuthToken.objects.create(
                        token = request.facebook.signed_request.user.oauth_token.token,
                        issued_at = request.facebook.signed_request.user.oauth_token.issued_at.replace(tzinfo=tzlocal()),
                        expires_at = request.facebook.signed_request.user.oauth_token.expires_at.replace(tzinfo=tzlocal())
                    )

                    user = User.objects.create(
                        facebook_id = request.facebook.signed_request.user.id,
                        oauth_token = oauth_token
                    )

                    user.synchronize()

                # Update the user's details and OAuth token
                else:
                    user.last_seen_at = now()

                    if 'signed_request' in request.REQUEST:
                        user.authorized = True

                        if request.facebook.signed_request.user.oauth_token:
                            user.oauth_token.token = request.facebook.signed_request.user.oauth_token.token
                            user.oauth_token.issued_at = request.facebook.signed_request.user.oauth_token.issued_at.replace(tzinfo=tzlocal())
                            user.oauth_token.expires_at = request.facebook.signed_request.user.oauth_token.expires_at.replace(tzinfo=tzlocal())
                            user.oauth_token.save()

                    user.save()

                if not user.oauth_token.extended:
                    # Attempt to extend the OAuth token, but ignore exceptions raised by
                    # bug #102727766518358 in the Facebook Platform.
                    #
                    # http://developers.facebook.com/bugs/102727766518358/
                    try:
                        user.oauth_token.extend()
                    except:
                        pass

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
        if FANDJANGO_CACHE_SIGNED_REQUEST:
            if 'signed_request' in request.REQUEST:
                response.set_cookie('signed_request', request.REQUEST['signed_request'])
            response['P3P'] = 'CP="IDC CURa ADMa OUR IND PHY ONL COM STA"'
        return response

