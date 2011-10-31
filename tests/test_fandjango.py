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

    # test sending only user_id
    signed_request_user_1 = create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, user_id=1, issued_at=1254459601)
    assert signed_request_user_1 == 'Y0ZEAYY9tGklJimbbSGy2dgpYz9qZyVJp18zrI9xQY0=.eyJpc3N1ZWRfYXQiOiAxMjU0NDU5NjAxLCAidXNlcl9pZCI6IDEsICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYifQ=='

    data_user_1 = parse_signed_request(signed_request_user_1, FACEBOOK_APPLICATION_SECRET_KEY)
    assert sorted(data_user_1.keys()) == sorted([u'user_id', u'algorithm', u'issued_at'])
    assert data_user_1['user_id'] == 1
    assert data_user_1['algorithm'] == 'HMAC-SHA256'

    # test not sending a user_id which will default to user_id 1
    signed_request_user_2 = create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, issued_at=1254459601)
    assert signed_request_user_1 == signed_request_user_2

    # test sending each available named argument
    today = datetime.now()
    tomorrow = today + timedelta(hours=1)

    signed_request_user_3 = create_signed_request(
       app_secret = FACEBOOK_APPLICATION_SECRET_KEY,
       user_id = 999,
       issued_at = 1254459600,
       expires = tomorrow,
       oauth_token = '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk',
       app_data = {},
       page = {
           'id': '1',
           'liked': True
       }
   )

    data_user_3 = parse_signed_request(signed_request_user_3, FACEBOOK_APPLICATION_SECRET_KEY)
    assert sorted(data_user_3.keys()) == sorted([u'user_id', u'algorithm', u'issued_at', u'expires', u'oauth_token', u'app_data', u'page'])
    assert data_user_3['user_id'] == 999
    assert data_user_3['algorithm'] == 'HMAC-SHA256'
    assert data_user_3['issued_at'] == 1254459600
    assert data_user_3['expires'] == int(time.mktime(tomorrow.timetuple()))
    assert data_user_3['oauth_token'] == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert data_user_3['app_data'] == {}
    assert data_user_3['page'] == {
       'id': '1',
       'liked': True
    }


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
