from nose.tools import with_setup

from datetime import timedelta

from django.test.client import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.conf import settings

from fandjango.middleware import FacebookMiddleware
from fandjango.models import User
from fandjango.models import OAuthToken
from fandjango.utils import get_post_authorization_redirect_url

from .helpers import assert_contains

from facepy import GraphAPI, SignedRequest

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    def now():
        return datetime.now()

TEST_APPLICATION_ID     = '181259711925270'
TEST_APPLICATION_SECRET = '214e4cb484c28c35f18a70a3d735999b'
TEST_SIGNED_REQUEST     = 'MJ1IzETiVz6zwqm2K-AxFjXxThBTwKCTU2Hmc6yMiMI.eyJh' \
                          'bGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImV4cGlyZXMiOjEz' \
                          'NDEzMjQwMDAsImlzc3VlZF9hdCI6MTM0MTMxOTE4Niwib2F1' \
                          'dGhfdG9rZW4iOiJBQUFDazJ0Qzl6QllCQUw1UkVQUG5iYjF5' \
                          'OVpDcHgxcXdpZG5XWkFhMnRhbjNqWkJocEJhNVB4T3VyQmpa' \
                          'QlgwbXlzck9tbHBWSVUwT2daQ3FDcTUwajRiWkFVQTlQQzlX' \
                          'MVFlQUwyOFpDMFZMd1pEWkQiLCJ1c2VyIjp7ImNvdW50cnki' \
                          'OiJubyIsImxvY2FsZSI6ImVuX0dCIiwiYWdlIjp7Im1pbiI6' \
                          'MjF9fSwidXNlcl9pZCI6IjU4NjA1MjMzNiJ9'

call_command('syncdb', interactive=False)
call_command('migrate', interactive=False)

request_factory = RequestFactory()

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_method_override():
    """
    Verify that the request method is overridden
    from POST to GET if it contains a signed request.
    """
    facebook_middleware = FacebookMiddleware()

    request = request_factory.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    facebook_middleware.process_request(request)

    assert request.method == 'GET'

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_application_authorization():
    """
    Verify that the user is redirected to authorize the application
    upon querying a view decorated by ``facebook_authorization_required``
    sans signed request.
    """
    client = Client()

    response = client.get(
        path = reverse('home')
    )

    # There's no way to derive the view the response originated from in Django,
    # so verifying its status code will have to suffice.
    assert response.status_code == 401

    response = client.get(
        path = reverse('redirect')
    )

    # Verify that the URL the user is redirected to will in turn redirect to
    # "http://example.org".
    assert_contains("example.org", response.content)

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_application_authorization_with_additional_permissions():
    """
    Verify that the user is redirected to authorize the application upon querying a view
    decorated by ``facebook_authorization_required`` and a list of additional
    permissions sans signed request.
    """
    client = Client()

    response = client.get(
        path = reverse('places')
    )

    # There's no way to derive the view the response originated from in Django,
    # so verifying its status code will have to suffice.
    assert response.status_code == 401

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_authorization_denied():
    """
    Verify that the view referred to by AUTHORIZATION_DENIED_VIEW is
    rendered upon refusing to authorize the application.
    """    
    client = Client()

    response = client.get(
        path = reverse('home'),
        data = {
            'error': 'access_denied'
        }
    )

    # There's no way to derive the view the response originated from in Django,
    # so verifying its status code will have to suffice.
    assert response.status_code == 403

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_application_deauthorization():
    """
    Verify that users are marked as deauthorized upon
    deauthorizing the application.
    """
    client = Client()

    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)
    assert user.authorized == True

    response = client.post(
        path = reverse('deauthorize_application'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)
    assert user.authorized == False

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_signed_request_renewal():
    """
    Verify that users are redirected to renew their signed requests
    once they expire.
    """
    client = Client()

    signed_request = SignedRequest(TEST_SIGNED_REQUEST, TEST_APPLICATION_SECRET)
    signed_request.user.oauth_token.expires_at = now() - timedelta(days=1)

    response = client.get(
        path = reverse('home'),
        data = {
            'signed_request': signed_request.generate()
        }
    )

    # There's no way to derive the view the response originated from in Django,
    # so verifying its status code will have to suffice.
    assert response.status_code == 401

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_registration():
    """
    Verify that authorizing the application will register a new user.
    """
    client = Client()

    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    assert user.first_name == user.graph.get('me')['first_name']
    assert user.last_name == user.graph.get('me')['last_name']
    assert user.url == user.graph.get('me')['link']

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_user_synchronization():
    """
    Verify that users may be synchronized.
    """
    client = Client()

    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    user.synchronize()

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_user_permissions():
    """
    Verify that users maintain a list of permissions granted to the application.
    """
    client = Client()

    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    assert 'installed' in user.permissions

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_extend_oauth_token():
    """
    Verify that OAuth access tokens may be extended.
    """
    client = Client()

    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    user.oauth_token.extend()

    # Facebook doesn't extend access tokens for test users, so asserting
    # the expiration time will have to suffice.
    assert user.oauth_token.expires_at

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_get_post_authorization_redirect_url():
    """
    Verify that Fandjango redirects the user correctly upon authorizing the application.
    """
    request = request_factory.get('/foo/bar/baz')
    redirect_url = get_post_authorization_redirect_url(request)

    assert redirect_url == 'http://apps.facebook.com/fandjango-test/bar/baz'
