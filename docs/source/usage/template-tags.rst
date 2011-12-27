.. _template-tags:

Template tags
=============

Fandjango provides a template tag for loading and initializing Facebook's `JavaScript SDK`_::

    {% load facebook %}

    {% facebook_init %}
        // This code will be run once the JavaScript SDK has been loaded and initialized.
        alert('It worked!');
    {% endfacebook %}
    
.. admonition:: See also

    `Facebook's documentation on the JavaScript SDK <http://developers.facebook.com/docs/reference/javascript/>`_

.. _JavaScript SDK: http://developers.facebook.com/docs/reference/javascript/
