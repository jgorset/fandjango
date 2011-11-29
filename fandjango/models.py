from httplib import HTTPConnection
from datetime import datetime

from django.db import models

from fandjango.utils import cached_property as cached

from facepy import GraphAPI

import requests

class Facebook:
    """
    Facebook instances hold information on the current user and
    the page he/she is accessing the application from, as well as
    the signed request that information is derived from.

    Properties:
    user -- A User instance.
    signed_request -- A string describing the raw signed request.
    """

    user = None
    signed_request = None

class User(models.Model):
    """
    Instances of the User class represent Facebook users who have authorized the application.

    Properties:
    facebook_id -- An integer describing the user's Facebook ID.
    first_name -- A string describing the user's first name.
    middle_name -- A string describing the user's middle name.
    last_name -- A string describing the user's last name.
    verified - A boolean describing whether or not the user is verified by Facebook.
    birthday - A datetime object describing the user's birthday (requires 'user_birthday' extended permission)
    authorized - A boolean describing whether or not the user has currently authorized your application.
    oauth_token - An OAuth Token object.
    created_at - A datetime object describing when the user was registered.
    """

    facebook_id = models.BigIntegerField(unique=True)
    facebook_username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    authorized = models.BooleanField(default=True)
    oauth_token = models.OneToOneField('OAuthToken')
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        """Return the user's first name."""
        if self.first_name and self.middle_name and self.last_name:
            return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)

    @property
    @cached(seconds=60*60*24)
    def url(self):
        """
        Return a string describing the URL to the user's Facebook profile (see `Facebook Graph API Reference`_).

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('link', None)

    @property
    @cached(seconds=60*60*24)
    def gender(self):
        """
        Return a string describing the user's gender (see `Facebook Graph API Reference`_).

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('gender', None)

    @property
    @cached(seconds=60*60*24)
    def hometown(self):
        """
        Return a dictionary describing the user's hometown (see `Facebook Graph API Reference`_).

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('hometown', None)

    @property
    @cached(seconds=60*60*24)
    def location(self):
        """
        Return a dictionary describing the user's location (see `Facebook Graph API Reference`_).

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('location', None)

    @property
    @cached(seconds=60*60*24)
    def bio(self):
        """
        Return a string describing the user's bio (see `Facebook Graph API Reference`_).

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('bio', None)

    @property
    @cached(seconds=60*60*24)
    def relationship_status(self):
        """
        Return a dictionary describing the user's relationship status (see `Facebook Graph API Reference`_)

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('relationship_status', None)

    @property
    @cached(seconds=60*60*24)
    def political_views(self):
        """
        Return a string describing the user's political views (see `Facebook Graph API Reference`_)

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('political', None)

    @property
    @cached(seconds=60*60*24)
    def email(self):
        """
        Return a string describing the user's email (see `Facebook Graph API Reference`_)

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('email', None)

    @property
    @cached(seconds=60*60*24)
    def website(self):
        """
        Return a string describing the user's website (see `Facebook Graph API Reference`_)

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('website', None)

    @property
    @cached(seconds=60*60*24)
    def locale(self):
        """
        Return a string describing the user's locale (see `Facebook Graph API Reference`_)

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('locale', None)

    @property
    @cached(seconds=60*60*24)
    def timezone(self):
        """
        Return an integer describing the user's timezone (see `Facebook Graph API Reference`_)

        .. _Facebook Graph API Reference: https://developers.facebook.com/docs/reference/api/user/
        """
        return self.graph.get('me').get('timezone', None)

    @property
    @cached(seconds=60*60*24)
    def picture(self):
        """
        Return a string describing the URL to the user's profile picture.
        """
        return requests.get('http://graph.facebook.com/%s/picture' % self.facebook_id).url

    @property
    @cached(seconds=60*60*24)
    def verified(self):
        """
        Return a boolean describing whether the user is verified by Facebook.
        """
        return self.graph.get('me').get('verified', None)

    @property
    def graph(self):
        """Return a GraphAPI instance with the user's access token."""
        return GraphAPI(self.oauth_token.token)

    def synchronize(self):
        """Synchronize model fields."""
        profile = self.graph.get('me')

        self.facebook_username = profile.get('username')
        self.first_name = profile.get('first_name')
        self.middle_name = profile.get('middle_name')
        self.last_name = profile.get('last_name')
        self.birthday = datetime.strptime(profile['birthday'], '%m/%d/%Y') if profile.has_key('birthday') else None
        self.save()

    def __unicode__(self):
        if self.full_name:
            return u'%s' % self.full_name
        elif self.facebook_username:
            return u'%s' % self.facebook_username
        else:
            return u'%s' % self.facebook_id

class OAuthToken(models.Model):
    """
    Instances of the OAuthToken class are credentials used to query the Facebook API on behalf of a user.

    token -- A string describing the OAuth token itself.
    issued_at -- A datetime object describing when the token was issued.
    expires_at -- A datetime object describing when the token expires (or None if it doesn't)
    """

    token = models.CharField(max_length=255)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField(null=True, blank=True)

    @property
    def expired(self):
        return self.expires_at < datetime.now() if self.expires_at else False

    class Meta:
        verbose_name = 'OAuth token'
        verbose_name_plural = 'OAuth tokens'
