# Fandjango

## About

Fandjango is a Python library that makes it easier to make Facebook canvas
applications powered by Django.

## Requirements

Django

## Usage

Fandjango populates the request object with data derived from the signed
request Facebook sends canvas applications (see the [documentation on signed requests][1]).

[1]: http://developers.facebook.com/docs/authentication/canvas

If the client has authorized your application, `request.facebook` is a dictionary
with these keys:

* `user_id` - An integer describing the user's id on Facebook.
* `oauth_token` - A string describing the OAuth access token.
* `issued_at` - A datetime object describing when the OAuth token was issued.
* `expires_at` - A datetime object describing when the OAuth access token expires.

If the user has not authorized your application, `request.facebook` is `False`.

You can require a user to authorize your application before accessing a view with the
`facebook_authorization_required` decorator.

    from fandjango.decorators import facebook_authorization_required
    
    @facebook_authorization_required
    def foo(request, *args, **kwargs):
      [...]
      
This will redirect the request to the Facebook authorization dialog, which will in
turn redirect back to the original URI.

You can also redirect the request in a control flow of your own by using the
`redirect_to_facebook_authorization` function.

    from fandjango.utils import redirect_to_facebook_authorization
    
    def foo(request, *args, **kwargs):
      if not request.facebook:
        return redirect_to_facebook_authorization(redirect_uri='http://www.exampke.org/')
        
## Installation

* `pip install git+https://github.com/jgorset/fandjango`
* Add `fandjango.middleware.FacebookCanvasMiddleware` to your middleware classes.

## Configuration

Fandjango requires some constants to be set in your settings.py file:

* `FACEBOOK_APPLICATION_ID` - Your Facebook application's ID.
* `FACEBOOK_APPLICATION_SECRET_KEY` - Your Facebook application's secret key.
* `FACEBOOK_APPLICATION_URI` - Your application's canvas URI (ex. http://apps.facebook.com/my_application)
* `FACEBOOK_APPLICATION_INITIAL_PERMISSIONS` - An array of [extended permissions][2] to request upon authorizing the application (optional).

[2]: http://developers.facebook.com/docs/authentication/permissions

## Frequently asked questions

**Q:** *Do I need to pass the signed request around?*

**A:** No. Fandjango caches the latest signed request in a cookie so you don't have to worry about it.

**Q:** *What happens when the OAuth token expires?*

**A:** Fandjango will automatically renew the signed request once the OAuth token
expires. This is done by hijacking the request and redirecting the client to Facebook, which
in turn redirects the client back to the URI it was originally retrieving with a new signed
request attached.