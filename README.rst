Fandjango
=========

About
-----

Fandjango makes it really easy to create Facebook applications with Django.

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

Contribute
----------

* Fork the repository.
* Do your thing.
* Open a pull request.
* Receive cake.

I love you
----------

Johannes Gorset made this. You should `tweet me <http://twitter.com/jgorset>`_ if you can't get it
to work. In fact, you should tweet me anyway.
