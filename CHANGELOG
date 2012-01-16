CHANGELOG

4.0.2

- Fixed a bug that caused an AttributeError upon issuing a HTTP GET request to the deauthorization view.
- Fixed a bug that caused application deauthorization to fail.
- Fixed a bug that prevented the norwegian localization from being applied.

4.0.1

- Fixed a bug that caused an ImportError with FANDJANGO_ENABLED_PATHS or FANDJANGO_DISABLED_PATHS.
- Fixed a bug prevented templates from being installed.

4.0.0

- User#graph no longer supports Facebook's Python SDK.
- User#full_name, User#url, User#gender, User#hometown, User#location, User#bio, User#relationship_status,
  User#political_views, User#email, User#website, User#locale, User#timezone, User#picture and User#verified
  are no longer persisted, but queried from Facebook and cached for 24 hours.
- The request object's 'facebook' attribute now has a 'signed_request' attribute that contains the result
  of parsing the signed request with Facepy.
- The request object's 'facebook' attribute no longer has a 'page' attribute with information on
  the Facebook page the application was loaded from.
- Fixed a race condition that caused multiple records to be registered for the same user.
- Users that refuse to authorize the application will now be directed to the view referenced by
  the FANDJANGO_AUTHORIZATION_DENIED_VIEW setting.
- FACEBOOK_APPLICATION_CANVAS_URL is now FACEBOOK_APPLICATION_NAMESPACE.
- Facilitated for internationalization.
- Fandjango is now available in Norwegian.

3.7.4

- Added support for reverse-engineering signed requests.
- Added User#middle_name, User#timezone and User#quotes.

3.7.3

- Fixed a bug that produced HTTP 500, causing 'User#picture' to fail.
- 'request.POST' is now reset to an empty QueryDict instance after
  overriding the request method of Facebook's initial request
  from POST to GET.

3.7.2

- Fixed a bug that caused a KeyError when Facebook lists the user's hometown and location incorrectly.

3.7.1

- Fixed a bug that caused a TypeError in Django's admin for models that were linked to Fandjango's User model.

3.7.0

- You may now find an instance of your favourite Graph API client (provided your favourite is either
Facepy or Facebook's official Python SDK) initialized with the user's access token in 'User#graph'.
- You may now initialize Facebook's JavaScript SDK with the 'facebook_init' template tag.

3.6.3

- Fixed a bug that caused endless redirection for users who have granted the application offline access.

3.6.2

- Fixed a bug that caused Facebook Page profiles to raise an IntegrityError.
- Fixed a bug that caused Facebook Page profiles to display with full name 'None None' in the admin.

3.6.1

- Fixed a bug that caused the "facebook_authorization_required" decorator to be incompatible with Django libraries that modify
the order of arguments given to views.

3.6

- It is now possible to direct users to application authorization from templates: "{% url authorize_application %}".
- Fandjango now tracks whether users currently authorize the application (this requires some configuration; see the README for details).

3.5.0

- The user model has been upgraded with a number of new properties: facebook_username, hometown, location, bio,
relationship_status, political_views, email, website, locale, verified and birthday.
- You may now synchronize a user instance with Facebook by calling its synchronize() method.

3.4.1

- Fandjango now supports South database migrations. To enable South in an existing installation of Fandjango,
run 'python manage.py migrate fandajngo 0001 --fake'.

3.4.0

- New feature: FANDJANGO_ENABLED_PATHS
- New feature: FANDJANGO_DISABLED_PATHS
- FANDJANGO_IGNORE_PATHS is now deprecated.
- New feature: OAuthToken#expired
- The OAuth Token model is now registered with Django's admin.

3.3

- HTTP POST requests made from the Facebook platform as a result of Facebook's 'POST to Canvas' migration
are now transparently converted to HTTP GET requests.

3.2.2

- New feature: FANDJANGO_IGNORE_PATHS

3.2.1

- Fandjango is no longer dependant on Facebook's Python SDK.
- Fix ImportError exceptions introduced in 3.2.

3.2.0

- Fix a bug that caused an exception when the user had not specified his/her/its first name,
last name or gender.

3.1.1

- Fandjango now supports Python 2.5.

3.1.0

- The 'facebook_authorization_required' decorator now has an optional argument; 'redirect_uri'. Note
that this changes its syntax; it now requires to be suffixed by a set of parenthesis.

3.0.1

- Fixed a bug that caused Fandjango to crash if no signed request was available.

3.0.0

- Information previously found in 'request.facebook_page' and 'request.facebook_user' are now found
in 'request.facebook.page' and 'request.facebook.user', respectively.

2.2.0

- New feature: Facebook application tabs.
- The 'facebook_user' attribute of the request object is now set to 'None' if no signed request.
is availabe, or the user has not authorized the application.

2.1.0

- New feature: User#created_at.
- New feature: User#last_seen_at.
- New feature: User#picture.
- Fixed a bug that prevented renewed OAuth tokens to be discarded.
- Fandjango is now registered with Django's admin.

2.0.2

- Fix a bug that prevented the 'facebook_user' attribute of the request object from being
set to false if no signed request was found or the user had not authorized the application.

2.0.1

- Fix a bug that caused permanent OAuth tokens to have their expiry set incorrectly.

2.0.0

- Facebook users that have authorized the application are now automatically registered
in Fandjango's user model.

1.2.0

- Fixed a bug that caused an exception if the signed request did not contain an user ID.
- Fixed a bug that caused the expiry time of OAuth tokens to be incorrect.

1.1.0

- Fandjango now supports Facebook's "POST to Canvas" migration.
- FACEBOOK_APPLICATION_URI has been renamed to FACEBOOK_APPLICATION_URL for consistency.

1.0.1

- Fandjango's version number is now available in the VERSION constant.
- Fandjango is now compatible with browsers that have JavaScript disabled.

1.0.0

- Everything
