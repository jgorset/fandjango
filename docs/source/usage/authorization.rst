.. _authorization:

Authorization
=============

You may require users to authorize your application with the ``facebook_authorization_required``
decorator::

    from fandjango.decorators import facebook_authorization_required

    @facebook_authorization_required
    def view(request):
        ...

.. admonition:: See also

    `Facebook's documentation on authorization <http://developers.facebook.com/docs/authentication/>`_

You may govern which permissions the application will request upon authorization
by configuring the ``FACEBOOK_APPLICATION_INITIAL_PERMISSIONS`` setting::

    FACEBOOK_APPLICATION_INITIAL_PERMISSIONS = ['read_stream', publish_stream']

.. admonition:: See also

    `Facebook's documentation on permissions <http://developers.facebook.com/docs/reference/api/permissions/>`_

Users that refuse to authorize your application will be directed to the view referenced by the
``FANDJANGO_AUTHORIZATION_DENIED_VIEW`` setting, which defaults to rendering the template
found in ``fandjango/authorization_denied.html`` on your template path.

.. _users:

Users
-----

Fandjango saves users that have authorized your application in its ``User`` model and
references the current user in ``request.facebook.user``::

    def greet(request):
        """Greet the user (or not)."""
        if request.facebook.user:
            greeting = "Hi, %s!" % request.facebook.user.first_name
        else:
            greeting = "Go away, I don't know you."
            
        return HttpResponse(greeting)

.. autoclass:: fandjango.models.User
    :members:
    
.. autoclass:: fandjango.models.OAuthToken
    :members:
    

.. note::

    Only the user's ``facebook_id``, ``first_name``, ``middle_name``, ``last_name``,
    ``authorized``, ``oauth_token``, ``created_at`` and ``last_seen_at`` attributes are
    persisted. The remaining attributes are queried from Facebook and cached for 24
    hours.
    
.. note::

    In order to track whether users have currently authorized your application, you must
    configure your Facebook application's "Deauthorize Callback" to the URL of Fandjango's
    ``deauthorize_application`` view
    (e.g. ``http://example.com/fandjango/deauthorize_application.html).

If the user has not authorized your application, ``request.facebook.user`` is ``None``.
