from httplib import HTTPConnection
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _

from fandjango.utils import cached_property as cached

from facepy import GraphAPI

import requests

class Facebook:
    """
    Facebook instances hold information on the current user and
    his/her signed request.
    """

    user = None
    """A ``User`` instance."""

    signed_request = None
    """A ``SignedRequest`` instance."""

class User(models.Model):
    """
    Instances of the User class represent Facebook users who
    have authorized the application.
    """

    facebook_id = models.BigIntegerField(_('facebook id'), unique=True)
    """An integer describing the user's Facebook ID."""

    facebook_username = models.CharField(_('facebook username'), max_length=255, blank=True, null=True)
    """A string describing the user's Facebook username."""

    first_name = models.CharField(_('first name'), max_length=255, blank=True, null=True)
    """A string describing the user's first name."""

    middle_name = models.CharField(_('middle name'), max_length=255, blank=True, null=True)
    """A string describing the user's middle name."""

    last_name = models.CharField(_('last name'), max_length=255, blank=True, null=True)
    """A string describing the user's last name."""

    birthday = models.DateField(_('birthday'), blank=True, null=True)
    """A ``datetime`` object describing the user's birthday."""

    authorized = models.BooleanField(_('authorized'), default=True)
    """A boolean describing whether the user has currently authorized the application."""

    oauth_token = models.OneToOneField('OAuthToken', verbose_name=_('OAuth token'))
    """An ``OAuthToken`` object."""

    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    """A ``datetime`` object describing when the user was registered."""

    last_seen_at = models.DateTimeField(_('last seen at'), auto_now_add=True)
    """A ``datetime`` object describing when the user was last seen."""

    @property
    def full_name(self):
        """Return the user's first name."""
        if self.first_name and self.middle_name and self.last_name:
            return "%s %s %s" % (self.first_name, self.middle_name, self.last_name)
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)

    @property
    @cached(days=1)
    def url(self):
        """
        A string describing the URL to the user's Facebook profile.
        """
        return self.graph.get('me').get('link', None)

    @property
    @cached(days=1)
    def gender(self):
        """
        A string describing the user's gender.
        """
        return self.graph.get('me').get('gender', None)

    @property
    @cached(days=1)
    def hometown(self):
        """
        A dictionary describing the user's hometown.
        """
        return self.graph.get('me').get('hometown', None)

    @property
    @cached(days=1)
    def location(self):
        """
        A dictionary describing the user's location.
        """
        return self.graph.get('me').get('location', None)

    @property
    @cached(days=1)
    def bio(self):
        """
        A string describing the user's bio.
        """
        return self.graph.get('me').get('bio', None)

    @property
    @cached(days=1)
    def relationship_status(self):
        """
        A dictionary describing the user's relationship status.
        """
        return self.graph.get('me').get('relationship_status', None)

    @property
    @cached(days=1)
    def political_views(self):
        """
        A string describing the user's political views.
        """
        return self.graph.get('me').get('political', None)

    @property
    @cached(days=1)
    def email(self):
        """
        A string describing the user's email.
        """
        return self.graph.get('me').get('email', None)

    @property
    @cached(days=1)
    def website(self):
        """
        A string describing the user's website.
        """
        return self.graph.get('me').get('website', None)

    @property
    @cached(days=1)
    def locale(self):
        """
        A string describing the user's locale.
        """
        return self.graph.get('me').get('locale', None)

    @property
    @cached(days=1)
    def timezone(self):
        """
        An integer describing the user's timezone.
        """
        return self.graph.get('me').get('timezone', None)

    @property
    @cached(days=1)
    def picture(self):
        """
        A string describing the URL to the user's profile picture.
        """
        return requests.get('http://graph.facebook.com/%s/picture' % self.facebook_id).url

    @property
    @cached(days=1)
    def verified(self):
        """
        A boolean describing whether the user is verified by Facebook.
        """
        return self.graph.get('me').get('verified', None)

    @property
    def graph(self):
        """
        A ``Facepy.GraphAPI`` instance initialized with the user's access token (See `Facepy`_).

        .. _Facepy: http://github.com/jgorset/facepy
        """
        return GraphAPI(self.oauth_token.token)

    def synchronize(self):
        """
        Synchronize ``facebook_username``, ``first_name``, ``middle_name``,
        ``last_name`` and ``birthday`` with Facebook.
        """
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
            
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

class OAuthToken(models.Model):
    """
    Instances of the OAuthToken class are credentials used to query
    the Facebook API on behalf of a user.
    """

    token = models.TextField(_('token'))
    """A string describing the OAuth token itself."""
    
    issued_at = models.DateTimeField(_('issued at'))
    """A ``datetime`` object describing when the token was issued."""
    
    expires_at = models.DateTimeField(_('expires at'), null=True, blank=True)
    """A ``datetime`` object describing when the token expires (or ``None`` if it doesn't)"""

    @property
    def expired(self):
        return self.expires_at < datetime.now() if self.expires_at else False

    class Meta:
        verbose_name = _('OAuth token')
        verbose_name_plural = _('OAuth tokens')
