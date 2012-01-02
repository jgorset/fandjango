from nose.tools import with_setup

from datetime import datetime, timedelta

from django.test.client import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.management import call_command
from django.conf import settings

from fandjango.middleware import FacebookMiddleware
from fandjango.models import User
from fandjango.models import OAuthToken

from facepy import SignedRequest

TEST_ACCESS_TOKEN = 'AAACk2tC9zBYBAMQkPqG12toWs00QScH035lOvh9WURUQj8KTfo8FJTpqB9BAOSnrk7oR8WPUAhnrm8FGYIjyWNdcALANnZCzZCgXEYzVdRBNjgSPDC'

TEST_SIGNED_REQUEST = 'Dvr1fXNUwE6CzKkUT3wpLo_7Izpq6i3XtQEf96sfgss.eyJhbGdvcml0aG0' \
                      'iOiJITUFDLVNIQTI1NiIsImV4cGlyZXMiOjEzMjU1MjM2MDAsImlzc3VlZF' \
                      '9hdCI6MTMyNTUxODQ3MSwib2F1dGhfdG9rZW4iOiJBQUFDazJ0Qzl6QllCQ' \
                      'U1Ra1BxRzEydG9XczAwUVNjSDAzNWxPdmg5V1VSVVFqOEtUZm84RkpUcHFC' \
                      'OUJBT1Nucms3b1I4V1BVQWhucm04RkdZSWp5V05kY0FMQU5uWkN6WkNnWEV' \
                      'ZelZkUkJOamdTUERDIiwidXNlciI6eyJjb3VudHJ5Ijoibm8iLCJsb2NhbG' \
                      'UiOiJlbl9HQiIsImFnZSI6eyJtaW4iOjIxfX0sInVzZXJfaWQiOiIxMDAwM' \
                      'DMzMjIzMjk1OTEifQ'

TEST_APPLICATION_SECRET_KEY = '214e4cb484c28c35f18a70a3d735999b'

client = Client()

def setup():
    call_command('syncdb', interactive=False)
    call_command('migrate', interactive=False)

def flush_database():
    call_command('flush', interactive=False)

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

@with_setup(setup=None, teardown=flush_database)
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

@with_setup(setup=None, teardown=flush_database)
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

@with_setup(setup=None, teardown=flush_database)
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

@with_setup(setup=None, teardown=flush_database)
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

@with_setup(setup=None, teardown=flush_database)
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

    assert user.first_name == 'Lisa'
    assert user.middle_name == 'Amccbbcbieia'
    assert user.last_name == 'Panditstein'
    assert user.full_name == 'Lisa Amccbbcbieia Panditstein'
    assert user.gender == 'female'
    assert user.url == 'http://www.facebook.com/profile.php?id=100003322329591'
    
    token = OAuthToken.objects.get(id=1)

    assert token.token == TEST_ACCESS_TOKEN
    assert token.issued_at == datetime(2012, 01, 02, 9, 34, 31)
    assert token.expires_at == datetime(2012, 01, 02, 11, 00, 00)

@with_setup(setup=None, teardown=flush_database)
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

    assert user.url == 'http://www.facebook.com/profile.php?id=100003322329591'
    assert user.gender == 'female'
    assert user.hometown == None
    assert user.location == None
    assert user.bio == None
    assert user.relationship_status == None
    assert user.political_views == None
    assert user.email == None
    assert user.website == None
    assert user.locale == 'en_GB', user.locale
    assert user.timezone == 1
    assert user.picture == 'http://profile.ak.fbcdn.net/static-ak/rsrc.php/v1/y9/r/IB7NOFmPw2a.gif'
    assert user.verified == None

@with_setup(setup=None, teardown=flush_database)
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
