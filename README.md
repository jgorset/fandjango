# Fandjango

## About

Facebook applications are simply websites that load in iframes on Facebook. Facebook provide documents loaded
within these iframes with various data, such as information about the user accessing it or the Facebook Page
it is accessed from. This data is encapsulated in [signed requests](http://developers.facebook.com/docs/authentication/signed_request/).
Fandjango parses signed requests, abstracts the information contained within and populates the request object accordingly.

## Getting started

You may find a sample application and a walkthrough to replicate it at the [Fandjango Example](https://github.com/jgorset/fandjango-example) repository.

## Usage

### Users

Fandjango saves clients that have authorized your application in its `User` model. You may access
the corresponding model instance in `request.facebook.user`.

Instances of the `User` model have the following properties:

* `facebook_id` - An integer describing the user's Facebook ID.
* `facebook_username` - A string describing the user's Facebook username.
* `first_name` - A string describing the user's first name.
* `last_name` - A string describing the user's last name.
* `profile_url` - A string describing the URL to the user's Facebook profile.
* `gender` - A string describing the user's gender.
* `hometown` - A string describing the user's home town (requires 'user_hometown' extended permission).
* `location` - A string describing the user's current location (requires 'user_location' extended permission).
* `bio` - A string describing the user's "about me" field on Facebook (requires 'user\_about\_me' extended permission).
* `relationship_status` - A string describing the user's relationship status (requires 'user_relationships' extended permission).
* `political_views` - A string describing the user's political views (requires 'user\_religion\_politics' extended permission).
* `email` - A string describing the user's email address (requires 'email' extended permission).
* `website` - A string describing the user's website (requires 'user_website' extended permission).
* `picture` - A string describing the URL to the user's profile picture.
* `locale` - A string describing the user's locale.
* `verified` - A boolean describing whether or not the user is verified by Facebook.
* `birthday` - A datetime object describing the user's birthday (requires 'user_birthday' extended permission)
* `authorized` - A boolean describing whether or not the user has currently authorized your application.
* `oauth_token` - An OAuth Token object.
* `graph` - A pre-initialized instance of [Facebook's Python SDK](http://github.com/facebook/python-sdk) or [Facepy](http://github.com/jgorset/facepy).
* `created_at` - A datetime object describing when the user was registered.
* `last_seen_at` - A datetime object describing when the user was last seen.

You may synchronize these properties with Facebook at any time with the model's `synchronize` method.

`oauth_token` is an instance of the `OAuthToken` model, which has the following properties:

* `token` - A string describing the OAuth token itself.
* `issued_at` - A datetime object describing when the token was issued.
* `expires_at` - A datetime object describing when the token expires (or `None` if it doesn't)

If the client has not authorized your application, `request.facebook.user` is `None`.

#### Authorizing users

You may require a client to authorize your application before accessing a view with the
`facebook_authorization_required` decorator.

    from fandjango.decorators import facebook_authorization_required
    
    @facebook_authorization_required()
    def foo(request, *args, **kwargs):
        pass
      
This will redirect the request to the Facebook authorization dialog, which will in
turn redirect back to the original URI. The decorator accepts an optional argument `redirect_uri`,
allowing you to customize the location the user is redirected to after authorizing the application:

    from settings import FACEBOOK_APPLICATION_TAB_URL
    from fandjango.decorators import facebook_authorization_required
    
    @facebook_authorization_required(redirect_uri=FACEBOOK_APPLICATION_TAB_URL)
    def foo(request, *args, **kwargs):
        pass

If you prefer, you may redirect the request in a control flow of your own by using the
`redirect_to_facebook_authorization` function:

    from fandjango.utils import redirect_to_facebook_authorization
    
    def foo(request, *args, **kwargs):
        if not request.facebook.user:
            return redirect_to_facebook_authorization(redirect_uri='http://www.example.org/')
            
... or link to it from your template:

    [...]
    <a href="{% url authorize_application %}">Authorize application</a>
    [...]

### Pages

If the application is accessed from a tab on a Facebook Page, you'll find an instance of `FacebookPage`
in `request.facebook.page`.

Instances of the `FacebookPage` model have the following properties:

* `id` -- An integer describing the id of the page.
* `is_admin` -- A boolean describing whether or not the current user is an administrator of the page.
* `is_liked` -- A boolean describing whether or not the current user likes the page.
* `url` -- A string describing the URL to the page.

If the application is not accessed from a tab on a Facebook Page, `request.facebook.page` is `None`.

### Template tags

Fandjango provides a template tag for loading and initializing Facebook's JavaScript SDK:

    {% load facebook %}
    
    {% facebook_init %}
        # This code will be run once the JavaScript SDK has been loaded and initialized.
        alert('It worked!')
    {% endfacebook %}
        
## Installation

* `pip install fandjango`
* Add `fandjango` to `INSTALLED_APPS`
* Add `fandjango.middleware.FacebookMiddleware` to `MIDDLEWARE_CLASSES`
* Add `url(r'^fandjango/', include('fandjango.urls'))` to your project's root URL configuration.

*Note:* If you're using Django's built-in CSRF protection middleware, you need to make sure Fandjango's middleware precedes it.
Otherwise, Facebook's requests to your application will qualify cross-site request forgeries.

## Upgrading

You may have to change your database schema when you upgrade Fandjango. Thankfully, schema migrations for [South](http://south.aeracode.org/)
have been bundled with Fandjango since v3.4.1 and upgrading your database is as simple as running `./manage.py migrate fandjango`.

If you're not using South, you should start. If you don't want to, I suppose you could migrate your database schema
manually... but you'd be making things really hard on yourself.

## Configuration

Fandjango looks to your settings file for its configuration.

#### Required configuration

* `FACEBOOK_APPLICATION_ID` - Your Facebook application's ID.
* `FACEBOOK_APPLICATION_SECRET_KEY` - Your Facebook application's secret key.
* `FACEBOOK_APPLICATION_URL` - Your application's canvas URI (ex. http://apps.facebook.com/my_application).

#### Optional configuration

* `FACEBOOK_APPLICATION_INITIAL_PERMISSIONS` - A list of [extended permissions](http://developers.facebook.com/docs/authentication/permissions) to request upon authorizing the application (optional).
* `FANDJANGO_DISABLED_PATHS` - A list of regular expression patterns describing paths on which Fandjango should not act (optional). These
should typically be paths that are accessed outside of the Facebook Canvas, such as Django's admin site.
* `FANDJANGO_ENABLED_PATHS` - A list of regular expression patterns describing paths on which Fandjango should act (optional). If undefined,
Fandjango will operate on all paths.

If you'd like to track whether users currently authorize your application to interact with their accounts, you need to set the
"deauthorize callback" option in your application's settings on Facebook to "[...]/fandjango/deauthorize_application.html".

## Frequently asked questions

**Q:** *Do I need to pass the signed request around?*

**A:** No. Fandjango caches the latest signed request in a cookie so you don't have to worry about it.

**Q:** *Why does Django raise a CSRF exception when my application loads in the Facebook canvas?*

**A:** As of March 2011, Facebook's initial request to your application is a HTTP POST request that evaluates
to an attempt at cross-site request forgery by Django's built-in CSRF protection. Fandjango remedies this by
overriding the request method of POST requests that only contain a signed request to GET, but you need to make
sure that its middleware is loaded before Django's `CsrfViewMiddleware`.

**Q:** *Why does Fandjango set a new header called "P3P"?*

**A:** P3P (or *Platform for Privacy Preferences*) is a W3 standard that enables websites to express
their privacy practices in a standard format that can be retrieved automatically and interpreted easily
by user agents. While this is largely ignored by most browsers, Internet Explorer will ignore cookies
set by third-party websites (ie. websites loaded in iframes) unless it specifies some P3P policies.

You can read more about P3P at [w3.org][3].

[3]: http://www.w3.org/TR/P3P/

**Q:** *What happens when the OAuth token expires?*

**A:** Fandjango will automatically renew the signed request once the OAuth token
expires. It does this by hijacking the request and redirecting the client to Facebook, which
in turn redirects the client back to the URI it was originally retrieving with a new signed
request attached.
