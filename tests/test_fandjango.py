import pytest


TEST_ACCESS_TOKEN = 'AAACk2tC9zBYBAOHQLGqAZAjhIXZAIX0kwZB8xsG8ItaEIEK6EFZCvKaoVKhCAOWtBxaHZAXXNlpP9gDJbNNwwQlZBcZA7j8rFLYsUff8EyUJQZDZD'

TEST_SIGNED_REQUEST = '3JpMRg1-xmZAo9L7jZ2RhgSjVi8LCt5YkIxSSaNrGvE.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImV4' \
                      'cGlyZXMiOjAsImlzc3VlZF9hdCI6MTMyMDA2OTYyNywib2F1dGhfdG9rZW4iOiJBQUFDazJ0Qzl6QllCQU9I' \
                      'UUxHcUFaQWpoSVhaQUlYMGt3WkI4eHNHOEl0YUVJRUs2RUZaQ3ZLYW9WS2hDQU9XdEJ4YUhaQVhYTmxwUDln' \
                      'REpiTk53d1FsWkJjWkE3ajhyRkxZc1VmZjhFeVVKUVpEWkQiLCJ1c2VyIjp7ImNvdW50cnkiOiJubyIsImxv' \
                      'Y2FsZSI6ImVuX1VTIiwiYWdlIjp7Im1pbiI6MjF9fSwidXNlcl9pZCI6IjEwMDAwMzA5NzkxNDI5NCJ9'

def test_parse_signed_request():
    """
    Test parsing signed requests.
    """
    from django.conf import settings
    from fandjango.utils import parse_signed_request

    data = parse_signed_request(
        signed_request = TEST_SIGNED_REQUEST,
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
    )

    assert data['user_id'] == '100003097914294'
    assert data['algorithm'] == 'HMAC-SHA256'
    assert data['expires'] == 0
    assert data['oauth_token'] == 'AAACk2tC9zBYBAOHQLGqAZAjhIXZAIX0kwZB8xsG8ItaEIEK6EFZCvKaoVKhCAOWtBxaHZAXXNlpP9gDJbNNwwQlZBcZA7j8rFLYsUff8EyUJQZDZD'
    assert data['issued_at'] == 1320069627

def test_create_signed_request():
    """
    Test creating faux signed requests.
    """
    from django.conf import settings
    from fandjango.utils import create_signed_request
    from fandjango.utils import parse_signed_request
    from datetime import datetime, timedelta
    import time

    signed_request = create_signed_request(
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY,
        user_id = 1,
        issued_at = 1254459601
    )

    assert signed_request == 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAx' \
                             'MjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ=='

    parsed_signed_request = parse_signed_request(
        signed_request = signed_request,
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
    )

    assert 'issued_at' in parsed_signed_request
    assert parsed_signed_request['user_id'] == 1
    assert parsed_signed_request['algorithm'] == 'HMAC-SHA256'

    today = datetime.now()
    tomorrow = today + timedelta(hours=1)

    signed_request = create_signed_request(
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY,
        user_id = 999,
        issued_at = today,
        expires = tomorrow,
        oauth_token = '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk',
        app_data = {
            'foo': 'bar'
        },
        page = {
            'id': '1',
            'liked': True
        }
    )

    parsed_signed_request = parse_signed_request(
        signed_request = signed_request,
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
    )

    assert parsed_signed_request['user_id'] == 999
    assert parsed_signed_request['algorithm'] == 'HMAC-SHA256'
    assert parsed_signed_request['issued_at'] == int(time.mktime(today.timetuple()))
    assert parsed_signed_request['expires'] == int(time.mktime(tomorrow.timetuple()))
    assert parsed_signed_request['oauth_token'] == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert parsed_signed_request['app_data'] == { 'foo': 'bar' }
    assert parsed_signed_request['page'] == { 'id': '1', 'liked': True }

def test_get_facebook_profile():
    """
    Test querying Facebook's Graph API for a profile.
    """
    from fandjango.utils import get_facebook_profile

    data = get_facebook_profile(TEST_ACCESS_TOKEN)

    assert data['id'] == '100003097914294'
    assert data['first_name'] == 'Bob'
    assert data['middle_name'] == 'Amcjigiadbid'
    assert data['last_name'] == 'Alisonberg'
    assert data['name'] == 'Bob Amcjigiadbid Alisonberg'
    assert data['gender'] == 'male'
    assert data['link'] == 'http://www.facebook.com/profile.php?id=100003097914294'

def test_facebook_post_method_override():
    """
    Verify that the request method is overridden
    from POST to GET if it contains a signed request.
    """
    from django.test.client import RequestFactory
    from django.core.urlresolvers import reverse
    from fandjango.middleware import FacebookMiddleware

    # We can't test that the request method is overriden with django.test.client.Client,
    # so we'll need to generate the request and process it manually (not cool, Django).
    request = RequestFactory().post(reverse('home'), {'signed_request': TEST_SIGNED_REQUEST})
    FacebookMiddleware().process_request(request)

    assert request.method == 'GET'

def test_fandjango_registers_user():
    """
    Verify that a user is registered.
    """
    from django.test.client import Client
    from django.core.urlresolvers import reverse
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import User

    client = Client()
    client.post(reverse('home'), {'signed_request': TEST_SIGNED_REQUEST})

    user = User.objects.get(id=1)

    assert user.first_name == 'Bob'
    assert user.middle_name == 'Amcjigiadbid'
    assert user.last_name == 'Alisonberg'
    assert user.full_name == 'Bob Amcjigiadbid Alisonberg'
    assert user.gender == 'male'
    assert user.profile_url == 'http://www.facebook.com/profile.php?id=100003097914294'

def test_fandjango_registers_oauth_token():
    """
    Verify that an OAuth token is registered.
    """
    from django.test.client import Client
    from django.core.urlresolvers import reverse
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import OAuthToken
    from datetime import datetime

    client = Client()
    client.post(reverse('home'), {'signed_request': TEST_SIGNED_REQUEST})

    token = OAuthToken.objects.get(id=1)

    assert token.token == TEST_ACCESS_TOKEN
    assert token.issued_at == datetime(2011, 10, 31, 15, 0, 27)
    assert token.expires_at == None
