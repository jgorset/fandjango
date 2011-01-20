from django.db import models

class User(models.Model):
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
    token = models.CharField(max_length=255)
    issued_at = models.DateTimeField()
    expires_at = models.DateTimeField()