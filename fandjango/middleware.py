from datetime import datetime
from urllib import urlencode
import base64
import hmac
import hashlib
import json

from django.conf import settings

from utils import redirect_to_facebook_authorization

class FacebookCanvasMiddleware():
  """
  Middleware for Facebook canvas applications.
  
  FacebookCanvasMiddleware populates the request object with data for the current facebook user (see
  the process_request method for specifics).
  """
  
  def process_request(self, request):
    """
    Populate request.facebook with data derived from the signed request.
    
    For users who have authorized the application, this attribute is a dictionary with these keys:
    user_id -- An integer describing the user's id on Facebook.
    oauth_token -- A string describing the OAuth access token.
    issued_at -- A datetime object describing when the OAuth token was issued.
    expires_at -- A datetime object describing when the OAuth access token expires.
    
    If the OAuth token has expired at the time of the request, the client is redirected
    to Facebook to renew the signed request and then back to the original URI.
    
    For users who have not yet authorized the application, the attribute is set to False.
    
    """
    if 'signed_request' in request.REQUEST or 'signed_request' in request.COOKIES:
      facebook_data = _parse_signed_request(
        signed_request = request.REQUEST['signed_request'] if 'signed_request' in request.REQUEST else request.COOKIES['signed_request'],
        app_secret = settings.FACEBOOK_APPLICATION_SECRET_KEY
      )
      
      # A bug in Facebook platform causes it to send a timestamp rather than a number of seconds in the 'expires'
      # value of the signed request for application tabs.
      #
      # Until this issue is resolved, Fandjango detects whether 'expires' is a timestamp and replaces it
      # with the corresponding number of seconds if it is.
      if facebook_data.has_key('expires') and facebook_data['expires'] > 1262304000:
        facebook_data['expires'] = facebook_data['expires'] - time.time()

      if facebook_data.has_key('user_id'):
        request.facebook = {
          'issued_at': datetime.fromtimestamp(facebook_data['issued_at']),
          'user_id': facebook_data['user_id'],
          'expires_at': None if facebook_data['expires'] == 0 else datetime.fromtimestamp(facebook_data['issued_at'] + facebook_data['expires']),
          'oauth_token': facebook_data['oauth_token']
        }
        
        if request.facebook['expires_at'] and request.facebook['expires_at'] < datetime.now():
          return redirect_to_facebook_authorization(
            redirect_uri = settings.FACEBOOK_APPLICATION_URL + request.get_full_path()
          )
        
      else:
        request.facebook = False
    else:
      request.facebook = False


  def process_response(self, request, response):
    """
    Set compact P3P policies and save signed request to cookie.
    
    P3P is a WC3 standard (see http://www.w3.org/TR/P3P/), and although largely ignored by most
    browsers it is considered by IE before accepting third-party cookies (ie. cookies set by
    documents in iframes). If they are not set correctly, IE will not set these cookies.
    
    """
    if 'signed_request' in request.REQUEST:
      response.set_cookie('signed_request', request.REQUEST['signed_request'])
    response['P3P'] = 'CP="IDC CURa ADMa OUR IND PHY ONL COM STA"'
    return response

  
  
def _parse_signed_request(signed_request, app_secret):
    """Return dictionary with signed request data."""
    try:
      l = signed_request.split('.', 2)
      encoded_sig = str(l[0])
      payload = str(l[1])
    except IndexError:
      raise ValueError("Signed request malformed")
    
    sig = base64.urlsafe_b64decode(encoded_sig + "=" * ((4 - len(encoded_sig) % 4) % 4))
    data = base64.urlsafe_b64decode(payload + "=" * ((4 - len(payload) % 4) % 4))

    data = json.loads(data)

    if data.get('algorithm').upper() != 'HMAC-SHA256':
      raise ValueError("Signed request is using an unknown algorithm")
    else:
      expected_sig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
      raise ValueError("Signed request signature mismatch")
    else:
      return data
