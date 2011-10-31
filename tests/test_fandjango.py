import pytest
import mock_django

TEST_ACCESS_TOKEN = 'AAACk2tC9zBYBAOHQLGqAZAjhIXZAIX0kwZB8xsG8ItaEIEK6EFZCvKaoVKhCAOWtBxaHZAXXNlpP9gDJbNNwwQlZBcZA7j8rFLYsUff8EyUJQZDZD'

TEST_SIGNED_REQUEST = '3JpMRg1-xmZAo9L7jZ2RhgSjVi8LCt5YkIxSSaNrGvE.eyJhbGdvcml0aG0iOiJITUFDLVNIQTI1NiIsImV4' \
                      'cGlyZXMiOjAsImlzc3VlZF9hdCI6MTMyMDA2OTYyNywib2F1dGhfdG9rZW4iOiJBQUFDazJ0Qzl6QllCQU9I' \
                      'UUxHcUFaQWpoSVhaQUlYMGt3WkI4eHNHOEl0YUVJRUs2RUZaQ3ZLYW9WS2hDQU9XdEJ4YUhaQVhYTmxwUDln' \
                      'REpiTk53d1FsWkJjWkE3ajhyRkxZc1VmZjhFeVVKUVpEWkQiLCJ1c2VyIjp7ImNvdW50cnkiOiJubyIsImxv' \
                      'Y2FsZSI6ImVuX1VTIiwiYWdlIjp7Im1pbiI6MjF9fSwidXNlcl9pZCI6IjEwMDAwMzA5NzkxNDI5NCJ9'

def test_parse_signed_request():
    from mock_django.settings import FACEBOOK_APPLICATION_SECRET_KEY
    from fandjango.utils import parse_signed_request

    data = parse_signed_request(TEST_SIGNED_REQUEST, FACEBOOK_APPLICATION_SECRET_KEY)

    assert data['user_id'] == '100003097914294'
    assert data['algorithm'] == 'HMAC-SHA256'
    assert data['expires'] == 0
    assert data['oauth_token'] == 'AAACk2tC9zBYBAOHQLGqAZAjhIXZAIX0kwZB8xsG8ItaEIEK6EFZCvKaoVKhCAOWtBxaHZAXXNlpP9gDJbNNwwQlZBcZA7j8rFLYsUff8EyUJQZDZD'
    assert data['issued_at'] == 1320069627

def test_create_signed_request():
    from mock_django.settings import FACEBOOK_APPLICATION_SECRET_KEY
    from fandjango.utils import create_signed_request
    from fandjango.utils import parse_signed_request
    from datetime import datetime, timedelta
    import time

    signed_request = create_signed_request(
        app_secret = FACEBOOK_APPLICATION_SECRET_KEY,
        user_id = 1,
        issued_at = 1254459601
    )

    assert signed_request == 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAx' \
                             'MjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ=='

    parsed_signed_request = parse_signed_request(
        signed_request = signed_request,
        app_secret = FACEBOOK_APPLICATION_SECRET_KEY
    )

    assert 'issued_at' in parsed_signed_request
    assert parsed_signed_request['user_id'] == 1
    assert parsed_signed_request['algorithm'] == 'HMAC-SHA256'

    today = datetime.now()
    tomorrow = today + timedelta(hours=1)

    signed_request = create_signed_request(
        app_secret = FACEBOOK_APPLICATION_SECRET_KEY,
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
        app_secret = FACEBOOK_APPLICATION_SECRET_KEY
    )

    assert parsed_signed_request['user_id'] == 999
    assert parsed_signed_request['algorithm'] == 'HMAC-SHA256'
    assert parsed_signed_request['issued_at'] == int(time.mktime(today.timetuple()))
    assert parsed_signed_request['expires'] == int(time.mktime(tomorrow.timetuple()))
    assert parsed_signed_request['oauth_token'] == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert parsed_signed_request['app_data'] == { 'foo': 'bar' }
    assert parsed_signed_request['page'] == { 'id': '1', 'liked': True }

def test_get_facebook_profile():
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
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware

    request = RequestFactory().post('/', {'signed_request': TEST_SIGNED_REQUEST})
    FacebookMiddleware().process_request(request)

    assert request.method == 'GET'

def test_fandjango_registers_user():
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import User

    request = RequestFactory().post('/', {'signed_request': TEST_SIGNED_REQUEST})
    FacebookMiddleware().process_request(request)

    user = User.objects.get(id=1)

    assert user.first_name == 'Bob'
    assert user.last_name == 'Alisonberg'
    assert user.full_name == 'Bob Alisonberg'
    assert user.gender == 'male'
    assert user.profile_url == 'http://www.facebook.com/profile.php?id=100003097914294'

def test_fandjango_registers_oauth_token():
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import OAuthToken
    from datetime import datetime

    request = RequestFactory().post('/', {'signed_request': TEST_SIGNED_REQUEST})
    FacebookMiddleware().process_request(request)

    token = OAuthToken.objects.get(id=1)

    assert token.token == 'AAACk2tC9zBYBAOHQLGqAZAjhIXZAIX0kwZB8xsG8ItaEIEK6EFZCvKaoVKhCAOWtBxaHZAXXNlpP9gDJbNNwwQlZBcZA7j8rFLYsUff8EyUJQZDZD'
    assert token.issued_at == datetime(2011, 10, 31, 9, 0, 27)
    assert token.expires_at == None
