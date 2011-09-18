import pytest
import mock_django

TEST_ACCESS_TOKEN = '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'

TEST_SIGNED_REQUEST = 'mnrG8Wc9CH_rh-GCqq97GFAPOh6AY7cMO8IYVKb6Pa4.eyJhbGdvcml0aG0iOi' \
                      'JITUFDLVNIQTI1NiIsImV4cGlyZXMiOjAsImlzc3VlZF9hdCI6MTMwNjE3OTkw' \
                      'NCwib2F1dGhfdG9rZW4iOiIxODEyNTk3MTE5MjUyNzB8MTU3MGE1NTNhZDY2MD' \
                      'U3MDVkMWI3YTVmLjEtNDk5NzI5MTI5fDhYcU1SaENXREt0cEctaV96UmtIQkRT' \
                      'c3FxayIsInVzZXIiOnsiY291bnRyeSI6Im5vIiwibG9jYWxlIjoiZW5fVVMiLC' \
                      'JhZ2UiOnsibWluIjoyMX19LCJ1c2VyX2lkIjoiNDk5NzI5MTI5In0'

def test_parse_signed_request():
    from mock_django.settings import FACEBOOK_APPLICATION_SECRET_KEY
    from fandjango.utils import parse_signed_request

    data = parse_signed_request(TEST_SIGNED_REQUEST, FACEBOOK_APPLICATION_SECRET_KEY)

    assert data['user_id'] == '499729129'
    assert data['algorithm'] == 'HMAC-SHA256'
    assert data['expires'] == 0
    assert data['oauth_token'] == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert data['issued_at'] == 1306179904

def test_create_signed_request():
    from mock_django.settings import FACEBOOK_APPLICATION_SECRET_KEY
    from fandjango.utils import create_signed_request
    from fandjango.utils import parse_signed_request
    import pytest

    # test sending a facebook uid
    signed_request_user_1 = create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, 1)
    assert signed_request_user_1 == '2ZEHvNnxJi5Yx9g6znqKFQOAWPmPKyakKvpgn_PH0Es=.eyJpc3N1ZWRfYXQiOiAxMzA2MTc5OTA0LCAib2F1dGhfdG9rZW4iOiAiMTgxMjU5NzExOTI1MjcwfDE1NzBhNTUzYWQ2NjA1NzA1ZDFiN2E1Zi4xLTQ5OTcyOTEyOXw4WHFNUmhDV0RLdHBHLWlfelJrSEJEU3NxcWsiLCAiZXhwaXJlcyI6IDAsICJ1c2VyX2lkIjogMSwgImFsZ29yaXRobSI6ICJITUFDLVNIQTI1NiJ9'

    data_user_1 = parse_signed_request(signed_request_user_1, FACEBOOK_APPLICATION_SECRET_KEY)
    assert data_user_1.keys().sort() == [u'user_id', u'algorithm', u'expires', u'oauth_token', u'issued_at'].sort()
    assert data_user_1['user_id'] == 1
    assert data_user_1['algorithm'] == 'HMAC-SHA256'
    assert data_user_1['expires'] == 0
    assert data_user_1['oauth_token'] == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert data_user_1['issued_at'] == 1306179904

    # test not sending a facebook uid which will default to uid 1
    signed_request_user_2 = create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY)
    assert signed_request_user_1 == signed_request_user_2

    # test sending a Dict to be used as JSON object payload
    user_3_json = {
        'user_id': 999,
        'algorithm': 'HMAC-SHA256',
        'foo': 'bar',
        'face': 'book'
    }
    signed_request_user_3 = create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, json_object=user_3_json)
    assert signed_request_user_3 == 'cYb_A-C8tgwweLedoNAlSx8g5seh-tgtu6oCyjduK58=.eyJmb28iOiAiYmFyIiwgInVzZXJfaWQiOiA5OTksICJhbGdvcml0aG0iOiAiSE1BQy1TSEEyNTYiLCAiZmFjZSI6ICJib29rIn0='

    data_user_3 = parse_signed_request(signed_request_user_3, FACEBOOK_APPLICATION_SECRET_KEY)
    assert data_user_3.keys().sort() == [u'user_id', u'algorithm', u'foo', u'face'].sort()
    assert data_user_3['user_id'] == 999
    assert data_user_3['algorithm'] == 'HMAC-SHA256'
    assert data_user_3['foo'] == 'bar'
    assert data_user_3['face'] == 'book'

    # test unsupported algorithm
    user_3_json['algorithm'] = 'HMAC-SHA512'
    with pytest.raises(NotImplementedError):
        create_signed_request(FACEBOOK_APPLICATION_SECRET_KEY, json_object=user_3_json)

def test_get_facebook_profile():
    from fandjango.utils import get_facebook_profile

    data = get_facebook_profile(TEST_ACCESS_TOKEN)

    assert data['id'] == '499729129'
    assert data['first_name'] == 'Helen'
    assert data['middle_name'] == 'Diigbiabi'
    assert data['last_name'] == 'Laverdetberg'
    assert data['name'] == 'Helen Diigbiabi Laverdetberg'
    assert data['gender'] == 'female'
    assert data['link'] == 'http://www.facebook.com/profile.php?id=499729129'

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

    assert user.first_name == 'Helen'
    assert user.last_name == 'Laverdetberg'
    assert user.full_name == 'Helen Laverdetberg'
    assert user.gender == 'female'
    assert user.profile_url == 'http://www.facebook.com/profile.php?id=499729129'

def test_fandjango_registers_oauth_token():
    from django.test.client import RequestFactory
    from fandjango.middleware import FacebookMiddleware
    from fandjango.models import OAuthToken
    from datetime import datetime

    request = RequestFactory().post('/', {'signed_request': TEST_SIGNED_REQUEST})
    FacebookMiddleware().process_request(request)

    token = OAuthToken.objects.get(id=1)

    assert token.token == '181259711925270|1570a553ad6605705d1b7a5f.1-499729129|8XqMRhCWDKtpG-i_zRkHBDSsqqk'
    assert token.issued_at == datetime(2011, 5, 23, 14, 45, 4)
    assert token.expires_at == None
