Fandjango
=========

About
-----

Fandjango makes it stupidly easy to create Facebook applications with Django.

Usage
-----

::

    @facebook_authorization_required
    def greet(request):
        return HttpResponse('Hi, %s!' % request.facebook.user.first_name)

If you'd like to create an application that's a little more elaborate, you should
`read the documentation <http://readthedocs.org/docs/fandjango>`_.

Installation
------------

::

    $ pip install fandjango
