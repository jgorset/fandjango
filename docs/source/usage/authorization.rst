.. _authorization:

Authorization
=============

You may require users to authorize your application with the
``facebook_authorization_required`` decorator::

    from fandjango.decorators import facebook_authorization_required

    @facebook_authorization_required
    def view(request):
        ...
        
.. note::

    If you prefer, you may direct the user to authorize the application in a control
    flow of your own by rendering the ``authorize_application`` view or referencing it
    in a template.

You may govern which `permissions`_ the application will request upon authorization
by configuring the ``FACEBOOK_APPLICATION_INITIAL_PERMISSIONS`` setting.

If the user refuses to authorize your application, the view referenced by the
``FANDJANGO_AUTHORIZATION_DENIED_VIEW`` setting will be rendered.

.. _permissions: http://developers.facebook.com/docs/reference/api/permissions/

Users
-----

Fandjango saves users that have authorized your application in its ``User`` model and
references the current user in ``request.facebook.user``.

.. autoclass:: fandjango.models.User
    :members:
