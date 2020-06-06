Fandjango
=========

Fandjango makes it really easy to create Facebook applications with Django.

Usage
-----

::

    @facebook_authorization_required
    def greet(request):
        return HttpResponse('Hi, %s!' % request.facebook.user.first_name)

If you'd like to create an application that's a little more elaborate, you should
`read the documentation <http://readthedocs.org/projects/fandjango>`_.

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

I love Schibsted
----------------

I work at Schibsted with a bunch of awesome folks who are all every bit as passionate about
good code as myself. If you're using this library, we probably want to hire you.
