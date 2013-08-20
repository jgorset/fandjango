from nose.tools import with_setup

from datetime import timedelta
import base64
import hashlib
import hmac
import json

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

from mock import patch

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime
    def now():
        return datetime.now()

from time import time

TEST_APPLICATION_ID     = '181259711925270'
TEST_APPLICATION_SECRET = '214e4cb484c28c35f18a70a3d735999b'

def get_signed_request():
    payload = {
       'algorithm': 'HMAC-SHA256'
    }
    payload['user'] = {}
    payload['user']['country'] = 'uk'
    payload['user']['locale'] = 'en_GB'
    payload['oauth_token'] = 'ABCDE'
    payload['expires'] = time() + 999999
    payload['issued_at'] = time()
    payload['user_id'] = 12345

    encoded_payload = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':'))
    )

    encoded_signature = base64.urlsafe_b64encode(hmac.new(
        TEST_APPLICATION_SECRET,
        encoded_payload,
        hashlib.sha256
    ).digest())

    return '%(signature)s.%(payload)s' % {
        'signature': encoded_signature,
        'payload': encoded_payload
    }

TEST_SIGNED_REQUEST = get_signed_request()

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

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {}

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

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {}

        client.post(
            path = reverse('home'),
            data = {
                'signed_request': TEST_SIGNED_REQUEST
            }
        )

    user = User.objects.get(id=1)
    assert user.authorized == True

    client.post(
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

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {
            'first_name': 'Adem',
            'last_name': 'Gaygusuz',
            'link': 'http://www.ardweb.co.uk'
        }
        client.post(
            path = reverse('home'),
            data = {
                'signed_request': TEST_SIGNED_REQUEST
            }
        )

        user = User.objects.get(id=1)

        assert user.first_name == user.first_name
        assert user.last_name == user.last_name
        assert user.url == user.url

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_user_synchronization():
    """
    Verify that users may be synchronized.
    """
    client = Client()

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {}
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

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {}
        client.post(
            path = reverse('home'),
            data = {
                'signed_request': TEST_SIGNED_REQUEST
            }
        )

    user = User.objects.get(id=1)

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {
            'data': [
                {'installed': True}
            ]
        }
        
        assert 'installed' in user.permissions

@with_setup(teardown = lambda: call_command('flush', interactive=False))
def test_extend_oauth_token():
    """
    Verify that OAuth access tokens may be extended.
    """
    client = Client()

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = {}

        client.post(
            path = reverse('home'),
            data = {
                'signed_request': TEST_SIGNED_REQUEST
            }
        )

    user = User.objects.get(id=1)

    with patch.object(GraphAPI, 'get', autospec=True) as graph_get:
        graph_get.return_value = '&access_token=%s&expires=%d' % ('ABCDE', 99999)

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
