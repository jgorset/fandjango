from httplib import HTTPConnection
from datetime import datetime

from django.db import models

class Facebook:
    """
    Facebook instances hold information on the current user and
    the page he/she is accessing the application from, as well as
    the signed request that information is derived from.
    
    Properties:
    user -- A User instance.
    page -- A FacebookPage instance.
    signed_request -- A string describing the raw signed request.
    """
    user, page, signed_request = [None] * 3

class FacebookPage:
    """
    FacebookPage instances represent Facebook Pages.
    
    Properties:
    id -- An integer describing the id of the page.
    is_admin -- A boolean describing whether or not the current user is an administrator of the page.
    is_liked -- A boolean describing whether or not the current user likes the page.
    url -- A string describing the URL to the page.
    """
    
    def __init__(self, id, is_admin, is_liked):
        self.id = id
        self.is_admin = is_admin
        self.is_liked = is_liked
        self.url = 'http://facebook.com/pages/-/%s' % self.id

class User(models.Model):
    """
    Instances of the User class represent Facebook users who have authorized the application.
    
    Properties:
    facebook_id -- An integer describing the user's Facebook ID.
    first_name -- A string describing the user's first name.
    last_name -- A string describing the user's last name.
    profile_url -- A string describing the URL to the user's Facebook profile.
    gender -- A string describing the user's gender.
    oauth_token -- An OAuth Token object.
    
    """
    
    facebook_id = models.BigIntegerField()
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    profile_url = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    oauth_token = models.OneToOneField('OAuthToken')
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
        
    @property
    def picture(self):
        connection = HTTPConnection('graph.facebook.com')
        connection.request('GET', '%s/picture' % self.facebook_id)
        response = connection.getresponse()
        return response.getheader('Location')
        
    def __unicode__(self):
        return self.full_name

        
        
        
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