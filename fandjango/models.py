from django.db import models

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
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    profile_url = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    oauth_token = models.OneToOneField('OAuthToken')
    
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
        
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