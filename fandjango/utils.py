from django.http import HttpResponse
from django.conf import settings

def redirect_to_facebook_authorization(redirect_uri):
  """
  Redirect the user to authorize the application.
  
  Redirection is done by rendering a JavaScript snippet that redirects the parent
  window to the authorization URI, since Facebook will not allow this inside an iframe.
  """
  request_variables = {
    'client_id': settings.FACEBOOK_APPLICATION_ID,
    'redirect_uri': redirect_uri
  }
  
  if hasattr(settings, 'FACEBOOK_APPLICATION_INITIAL_PERMISSIONS'):
    request_variables['scope'] = ', '.join(settings.FACEBOOK_APPLICATION_INITIAL_PERMISSIONS)
  
  urlencoded_request_variables = urlencode(request_variables)
  
  html = """
    <!DOCTYPE html>
    
    <html>
    
      <head>
        <script type="text/javascript">
          window.parent.location = "https://graph.facebook.com/oauth/authorize?%s";
        </script>
      </head>
      
      <body>
        <noscript>
          You must <a href="https://graph.facebook.com/oauth/authorize?%s">authorize the application</a> in order to continue.
        </noscript>
      </body>
    
    </html>
  """ % (urlencoded_request_variables, urlencoded_request_variables)
  
  return HttpResponse(html)