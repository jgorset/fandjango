import pytest

from datetime import datetime, timedelta

from django.test.client import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.conf import settings

from fandjango.middleware import FacebookMiddleware
from fandjango.models import User
from fandjango.models import OAuthToken

from facepy import SignedRequest

TEST_ACCESS_TOKEN = 'AAACk2tC9zBYBAOHQLGqAZAjhIXZAIX0kwZB8xsG8ItaEIEK6EFZCvKaoVKhCAOWtBxaHZAXXNlpP9gDJbNNwwQlZBcZA7j8rFLYsUff8EyUJQZDZD'

TEST_SIGNED_REQUEST = '3JpMRg1-xmZAo9L7jZ2RhgSjVi8LCt5YkIxSSaNrGvE.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImV4' \
                      'cGlyZXMiOjAsImlzc3VlZF9hdCI6MTMyMDA2OTYyNywib2F1dGhfdG9rZW4iOiJBQUFDazJ0Qzl6QllCQU9I' \
                      'UUxHcUFaQWpoSVhaQUlYMGt3WkI4eHNHOEl0YUVJRUs2RUZaQ3ZLYW9WS2hDQU9XdEJ4YUhaQVhYTmxwUDln' \
                      'REpiTk53d1FsWkJjWkE3ajhyRkxZc1VmZjhFeVVKUVpEWkQiLCJ1c2VyIjp7ImNvdW50cnkiOiJubyIsImxv' \
                      'Y2FsZSI6ImVuX1VTIiwiYWdlIjp7Im1pbiI6MjF9fSwidXNlcl9pZCI6IjEwMDAwMzA5NzkxNDI5NCJ9'
                      
TEST_APPLICATION_SECRET_KEY = '214e4cb484c28c35f18a70a3d735999b'

client = Client()

def test_method_override():
    """
    Verify that the request method is overridden
    from POST to GET if it contains a signed request.
    """

    # We can't test that the request method is overriden with django.test.client.Client,
    # so we'll need to generate the request and process it manually (not cool, Django).
    request = RequestFactory().post(reverse('home'), {'signed_request': TEST_SIGNED_REQUEST})
    FacebookMiddleware().process_request(request)

    assert request.method == 'GET'

def test_application_authorization():
    """
    Verify that the user is redirected to authorize the application
    upon querying a view decorated by ``facebook_authorization_required``
    sans signed request.
    """
    response = client.get(
        path = reverse('home')
    )

    assert response.status_code == 303

def test_authorization_denied():
    """
    Verify that the user receives HTTP 403 Forbidden upon
    refusing to authorize the application.
    """
    response = client.get(
        path = reverse('home'),
        data = {
            'error': 'access_denied'
        }
    )

    assert response.status_code == 403

def test_application_deauthorization():
    """
    Verify that the user is marked as deauthorized upon
    deauthorizing the application.
    """
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

def test_signed_request_renewal():
    """
    Verify that the user is redirected to renew his/her
    signed request if its access token has expired.
    """

    # Create an expired signed request
    parsed_signed_request = SignedRequest.parse(TEST_SIGNED_REQUEST, settings.FACEBOOK_APPLICATION_SECRET_KEY)
    parsed_signed_request.oauth_token.expires_at = datetime.now() - timedelta(days=1)
    expired_signed_request = parsed_signed_request.generate(settings.FACEBOOK_APPLICATION_SECRET_KEY)

    response = client.get(
        path = reverse('home'),
        data = {
            'signed_request': expired_signed_request
        }
    )

    assert response.status_code == 303

def test_registration():
    """
    Verify that a user and an OAuth token is registered upon
    querying the application with a signed request.
    """
    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    assert user.first_name == 'Bob'
    assert user.middle_name == 'Amcjigiadbid'
    assert user.last_name == 'Alisonberg'
    assert user.full_name == 'Bob Amcjigiadbid Alisonberg'
    assert user.gender == 'male'
    assert user.url == 'http://www.facebook.com/profile.php?id=100003097914294'
    
    token = OAuthToken.objects.get(id=1)

    assert token.token == TEST_ACCESS_TOKEN
    assert token.issued_at == datetime(2011, 10, 31, 15, 0, 27)
    assert token.expires_at == None

def test_user_details():
    """
    Verify that user details may be queried from Facebook.
    """
    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    assert user.url == 'http://www.facebook.com/profile.php?id=100003097914294'
    assert user.gender == 'male'
    assert user.hometown == None
    assert user.location == None
    assert user.bio == None
    assert user.relationship_status == None
    assert user.political_views == None
    assert user.email == None
    assert user.website == None
    assert user.locale == 'en_US'
    assert user.timezone == None
    assert user.picture == 'http://profile.ak.fbcdn.net/static-ak/rsrc.php/v1/yo/r/UlIqmHJn-SK.gif'
    assert user.verified == None

def test_user_synchronization():
    """
    Verify that users may be synchronized.
    """
    client.post(
        path = reverse('home'),
        data = {
            'signed_request': TEST_SIGNED_REQUEST
        }
    )

    user = User.objects.get(id=1)

    user.synchronize()
