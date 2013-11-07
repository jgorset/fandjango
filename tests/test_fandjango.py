from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import json
import unittest

from django.test.client import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.conf import settings

from fandjango.middleware import FacebookMiddleware, FacebookWebMiddleware
from fandjango.models import User, OAuthToken
from fandjango.utils import get_post_authorization_redirect_url

from .helpers import assert_contains

from facepy import GraphAPI, SignedRequest

from mock import patch

try:
    from django.utils.timezone import now
except ImportError:
    def now():
        return datetime.now()

from time import time

def get_signed_request():
    payload = {
       'algorithm': 'HMAC-SHA256',
       'user': {
         'country': 'uk',
         'locale': 'en_GB'
       },
       'oauth_token': 'ABCDE',
       'expires': time() + 999999,
       'issued_at': time(),
       'user_id': 12345
    }

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

TEST_APPLICATION_ID     = '181259711925270'
TEST_APPLICATION_SECRET = '214e4cb484c28c35f18a70a3d735999b'
TEST_SIGNED_REQUEST = get_signed_request()
TEST_AUTH_CODE = 'TEST_CODE'
TEST_ACCESS_TOKEN = 'ABCDE'
TEST_GRAPH_ACCESS_TOKEN_RESPONSE = '&access_token=%s&expires=%d' % ('ABCDE', 99999)
TEST_GRAPH_ME_RESPONSE = {
    'id': '12345',
    'username': 'foobar',
    'name': 'Foo Bar', 
    'first_name': 'Foo',
    'last_name': 'Bar',
    'birthday': '03/03/2000',
    'email': 'foo@bar.com',
    'locale': 'locale',
    'gender': 'gender',
    'link': 'http://www.foo.com'
}

call_command('syncdb', interactive=False)
call_command('migrate', interactive=False)

request_factory = RequestFactory()

class TestFacebookMiddleware(unittest.TestCase):
    
    def setUp(self):
        settings.MIDDLEWARE_CLASSES = [
            'fandjango.middleware.FacebookMiddleware'
        ]

    def tearDown(self):
        call_command('flush', interactive=False)

    def test_method_override(self):
        """
        Verify that the request method is overridden
        from POST to GET if it contains a signed request.
        """
        facebook_middleware = FacebookMiddleware()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = TEST_GRAPH_ME_RESPONSE

            request = request_factory.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

            facebook_middleware.process_request(request)

        assert request.method == 'GET'

    def test_application_authorization(self):
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

    def test_application_authorization_with_additional_permissions(self):
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

    def test_authorization_denied(self):
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

    def test_application_deauthorization(self):
        """
        Verify that users are marked as deauthorized upon
        deauthorizing the application.
        """

        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = TEST_GRAPH_ME_RESPONSE

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

    def test_signed_request_renewal(self):
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

    def test_registration(self):
        """
        Verify that authorizing the application will register a new user.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = TEST_GRAPH_ME_RESPONSE

            client.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

            user = User.objects.get(id=1)

            assert TEST_GRAPH_ME_RESPONSE['first_name'] == user.first_name
            assert TEST_GRAPH_ME_RESPONSE['last_name'] == user.last_name
            assert TEST_GRAPH_ME_RESPONSE['link'] == user.extra_data.get('link')

    def test_user_synchronization(self):
        """
        Verify that users may be synchronized.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = {}
            
            client.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

            user = User.objects.get(id=1)

            user.synchronize()

    def test_user_permissions(self):
        """
        Verify that users maintain a list of permissions granted to the application.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = {}

            client.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

        user = User.objects.get(id=1)

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = {
                'data': [
                    {'installed': True}
                ]
            }
            
            assert 'installed' in user.permissions

    def test_extend_oauth_token(self):
        """
        Verify that OAuth access tokens may be extended.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = {}

            client.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

        user = User.objects.get(id=1)

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = '&access_token=%s&expires=%d' % ('ABCDE', 99999)

            user.oauth_token.extend()

        # Facebook doesn't extend access tokens for test users, so asserting
        # the expiration time will have to suffice.
        assert user.oauth_token.expires_at

    def test_get_post_authorization_redirect_url(self):
        """
        Verify that Fandjango redirects the user correctly upon authorizing the application.
        """
        request = request_factory.get('/foo/bar/baz')
        redirect_url = get_post_authorization_redirect_url(request)

        assert redirect_url == 'http://apps.facebook.com/fandjango-test/bar/baz'

    def test_authed_user_doesnt_get_redirected(self):
        """
        Verify that authorizing the application will register a new user.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = TEST_GRAPH_ME_RESPONSE

            response = client.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

        assert response.status_code != 401

class TestFacebookWebMiddleware(unittest.TestCase):

    def setUp(self):
        settings.MIDDLEWARE_CLASSES = [
            'fandjango.middleware.FacebookWebMiddleware'
        ]

    def tearDown(self):
        call_command('flush', interactive=False)

    def test_application_authorization(self):
        """
        Verify that the user is redirected to authorize the application
        upon querying a view decorated by ``facebook_authorization_required``
        sans code nor access token.
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

    def test_application_authorization_with_additional_permissions(self):
        """
        Verify that the user is redirected to authorize the application upon querying a view
        decorated by ``facebook_authorization_required`` and a list of additional
        permissions sans code nor access token.
        """
        client = Client()

        response = client.get(
            path = reverse('places')
        )

        # There's no way to derive the view the response originated from in Django,
        # so verifying its status code will have to suffice.
        assert response.status_code == 401

    def test_authorization_denied(self):
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

    def test_oauth_token_request_renewal(self):
        """
        Verify that users are redirected to renew their access token
        once they expire.
        """
        client = Client()

        oauth_token = OAuthToken.objects.create(
            token = TEST_ACCESS_TOKEN,
            issued_at = now() - timedelta(days = 1),
            expires_at = now() - timedelta(days = 2)
        )

        client.cookies['oauth_token'] = oauth_token.token

        response = client.get(
            path = reverse('home')
        )

        # There's no way to derive the view the response originated from in Django,
        # so verifying its status code will have to suffice.
        assert response.status_code == 401

    def test_registration(self):
        """
        Verify that authorizing the application will register a new user.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

        user = User.objects.get(id=1)

        assert TEST_GRAPH_ME_RESPONSE['first_name'] == user.first_name
        assert TEST_GRAPH_ME_RESPONSE['last_name'] == user.last_name
        assert TEST_GRAPH_ME_RESPONSE['link'] == user.extra_data.get('link')

    def test_user_synchronization(self):
        """
        Verify that users may be synchronized.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

            user = User.objects.get(id=1)

            user.synchronize()

    def test_user_permissions(self):
        """
        Verify that users maintain a list of permissions granted to the application.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

        user = User.objects.get(id=1)

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = {
                'data': [
                    {'installed': True}
                ]
            }
            
            assert 'installed' in user.permissions

    def test_extend_oauth_token(self):
        """
        Verify that OAuth access tokens may be extended.
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

        user = User.objects.get(id=1)

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = TEST_GRAPH_ACCESS_TOKEN_RESPONSE

            user.oauth_token.extend()

        # Facebook doesn't extend access tokens for test users, so asserting
        # the expiration time will have to suffice.
        assert user.oauth_token.expires_at

    def test_get_post_authorization_redirect_url(self):
        """
        Verify that Fandjango redirects the user correctly upon authorizing the application.
        """
        request = request_factory.get('/foo/bar/baz')
        redirect_url = get_post_authorization_redirect_url(request, canvas = False)

        assert redirect_url == 'http://example.org/foo/bar/baz'

    def test_querystring_removal(self):
        """
        Facebook related querystring parameters are removed upon successful authentication
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            response = client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

        assert 'code=' not in response["Location"]

class TestFacebookMultipleMiddleware(unittest.TestCase):

    def setUp(self):
        settings.MIDDLEWARE_CLASSES = [
            'fandjango.middleware.FacebookMiddleware',
            'fandjango.middleware.FacebookWebMiddleware'
        ]

    def tearDown(self):
        call_command('flush', interactive=False)

    def test_registration(self):
        """
        User will register via signed request, skipping FacebookWebMiddleware
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:
            graph_get.return_value = TEST_GRAPH_ME_RESPONSE

            client.post(
                path = reverse('home'),
                data = {
                    'signed_request': TEST_SIGNED_REQUEST
                }
            )

            user = User.objects.get(id=1)

            assert TEST_GRAPH_ME_RESPONSE['first_name'] == user.first_name
            assert TEST_GRAPH_ME_RESPONSE['last_name'] == user.last_name
            assert TEST_GRAPH_ME_RESPONSE['link'] == user.extra_data.get('link')

    def test_web_registration(self):
        """
        User will register via FacebookWebMiddleware
        """
        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

        user = User.objects.get(id=1)

        assert TEST_GRAPH_ME_RESPONSE['first_name'] == user.first_name
        assert TEST_GRAPH_ME_RESPONSE['last_name'] == user.last_name
        assert TEST_GRAPH_ME_RESPONSE['link'] == user.extra_data.get('link')

    def test_deauthorized_user(self):
        """
        Check user cannot log in after deauthrorizing app.
        """

        client = Client()

        with patch.object(GraphAPI, 'get') as graph_get:

            def side_effect(*args, **kwargs):
                if args[0] == 'oauth/access_token':
                    return TEST_GRAPH_ACCESS_TOKEN_RESPONSE
                elif args[0] == 'me':
                    return TEST_GRAPH_ME_RESPONSE

            graph_get.side_effect = side_effect

            client.get(
                path = reverse('home'),
                data = {
                    'code': TEST_AUTH_CODE
                }
            )

        client.post(
            path = reverse('deauthorize_application'),
            data = {
                'signed_request': TEST_SIGNED_REQUEST
            }
        )

        client.cookies['signed_request'] = None

        response = client.get(
            path = reverse('home')
        )

        assert response.status_code == 401
