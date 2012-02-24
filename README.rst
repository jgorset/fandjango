Fandjango
=========

Fandjango makes it really easy to create Facebook applications with Django.

Usage
-----

You can require users to authorize your application by decorating views
with ``facebook_authorization_required``::

    @facebook_authorization_required
    def greet(request):
        return HttpResponse('Hi, %s!' % request.facebook.user.first_name)

You can prompt the user to grant your application privileges besides the defaults
by providing the decorator with a list of permissions::

    @facebook_authorization_required(permissions=['user_photos', 'user_relationships'])
    def stalk(request):
        for photo in request.facebook.user.graph.get("me/photos"):
            screensaver.add(photo)

If you'd like to create an application that's a little more elaborate (or a little less creepy), you should
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
