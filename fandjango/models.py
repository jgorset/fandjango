from httplib import HTTPConnection
from datetime import datetime

from django.db import models

from utils import get_facebook_profile
from django.utils import simplejson

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
    middle_name -- A string describing the user's middle name.
    last_name -- A string describing the user's last name.
    profile_url -- A string describing the URL to the user's Facebook profile.
    gender -- A string describing the user's gender.
    hometown - A string describing the user's home town (requires 'user_hometown' extended permission).
    location - A string describing the user's current location (requires 'user_location' extended permission).
    bio - A string describing the user's "about me" field on Facebook (requires 'user_about_me' extended permission).
    relationship_status - A string describing the user's relationship status (requires 'user_relationships' extended permission).
    political_views - A string describing the user's political views (requires 'user_religion_politics' extended permission).
    email - A string describing the user's email address (requires 'email' extended permission).
    website - A string describing the user's website (requires 'user_website' extended permission).
    locale - A string describing the user's locale.
    verified - A boolean describing whether or not the user is verified by Facebook.
    birthday - A datetime object describing the user's birthday (requires 'user_birthday' extended permission)
    authorized - A boolean describing whether or not the user has currently authorized your application.
    oauth_token - An OAuth Token object.
    created_at - A datetime object describing when the user was registered.
    oauth_token -- An OAuth Token object.
    timezone - Integer timezone representation, i.e. "GMT+2" would be just 2
    languages - Comma-separated list of languages
    activities - Comma-separated list of activities
    interests - Comma-separated list of interests
    inspirational_people - Comma-separated list of inspirational people
    sports - Comma-separated list of favorite  sports
    music - Comma-separated list of music
    movies - Comma-separated list of movies
    books - Comma-separated list of books
    television - Comma-separated list of television
    games - Comma-separated list of games
    geolocation - char field for more precise location, eg latitude/longitude
    quotes - Multiline string with favorite quotes
    likes - Multiline string with likes and cetegories
    """
    
    facebook_id = models.BigIntegerField()
    facebook_username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    profile_url = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    hometown = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    relationship_status = models.CharField(max_length=255, blank=True, null=True)
    political_views = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    website = models.CharField(max_length=255, blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True, null=True)
    verified = models.NullBooleanField()
    birthday = models.DateField(blank=True, null=True)
    authorized = models.BooleanField(default=True)
    oauth_token = models.OneToOneField('OAuthToken')
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now_add=True)
    timezone = models.IntegerField(blank=True, null=True)
    languages = models.CharField(max_length=255, blank=True, null=True)
    activities = models.CharField(max_length=255, blank=True, null=True)
    interests = models.CharField(max_length=255, blank=True, null=True)
    inspirational_people = models.CharField(max_length=255, blank=True, null=True)
    sports = models.CharField(max_length=255, blank=True, null=True)
    music = models.CharField(max_length=255, blank=True, null=True)
    movies = models.CharField(max_length=255, blank=True, null=True)
    books = models.CharField(max_length=255, blank=True, null=True)
    television = models.CharField(max_length=255, blank=True, null=True)
    games = models.CharField(max_length=255, blank=True, null=True)
    geolocation = models.CharField(max_length=255, blank=True, null=True)
    quotes = models.TextField(blank=True, null=True)
    likes = models.TextField(blank=True, null=True)
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return "%s %s" % (self.first_name, self.last_name)
        
    @property
    def picture(self):
        connection = HTTPConnection('graph.facebook.com')
        connection.request('GET', '/%s/picture' % self.facebook_id)
        response = connection.getresponse()
        return response.getheader('Location')
        
    @property
    def picture_large(self):
        " returns 200px wide, variable height image"
        connection = HTTPConnection('graph.facebook.com')
        connection.request('GET', '/%s/picture?type=large' % self.facebook_id)
        response = connection.getresponse()
        return response.getheader('Location')
    
    @property
    def picture_normal(self):
        "returns 100px wide, variable height image"
        connection = HTTPConnection('graph.facebook.com')
        connection.request('GET', '/%s/picture?type=normal' % self.facebook_id)
        response = connection.getresponse()
        return response.getheader('Location')
    
    @property
    def picture_small(self):
        "returns 50px wide, variable height image"
        connection = HTTPConnection('graph.facebook.com')
        connection.request('GET', '/%s/picture?type=small' % self.facebook_id)
        response = connection.getresponse()
        return response.getheader('Location')
    
    @property
    def picture_square(self):
        "returns 50x50px image"
        connection = HTTPConnection('graph.facebook.com')
        connection.request('GET', '/%s/picture?type=square' % self.facebook_id)
        response = connection.getresponse()
        return response.getheader('Location')
    
    @property
    def age(self):
        age = datetime.now().year - self.birthday.year if self.birthday else None
        return age
        
    def synchronize(self):
        """Synchronize the user with Facebook's Graph API."""
        if self.oauth_token.expired:
            raise ValueError('Signed request expired.')
        
        profile = get_facebook_profile(self.oauth_token.token)
        
        self.facebook_id = profile.get('id')
        self.facebook_username = profile.get('username')
        self.first_name = profile.get('first_name')
        self.middle_name = profile.get('middle_name', None)
        self.last_name = profile.get('last_name')
        self.profile_url = profile.get('link')
        self.gender = profile.get('gender')
        self.hometown = profile['hometown']['name'] if profile.has_key('hometown') else None
        self.location = profile['location']['name'] if profile.has_key('location') else None
        self.bio = profile.get('bio')
        self.relationship_status = profile.get('relationship_status')
        self.political_views = profile.get('political')
        self.email = profile.get('email')
        self.website = profile.get('website')
        self.locale = profile.get('locale')
        self.verified = profile.get('verified')
        self.birthday = datetime.strptime(profile['birthday'], '%m/%d/%Y') if profile.has_key('birthday') else None
        self.timezone = profile.get('timezone', None)
        self.quotes = profile.get('quotes', None)
        self.inspirational_people = ', '.join([element['name'] for element in profile['inspirational_people']]) if profile.has_key('inspirational_people') else None
        self.languages = ', '.join([element['name'] for element in profile['languages']]) if profile.has_key('languages') else None
        self.sports = ', '.join([element['name'] for element in profile['sports']]) if profile.has_key('sports') else None
        # getting extra objects using graph api
        self.activities = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/activities')])
        self.interests = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/interests')])
        self.music = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/music')])
        self.books = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/books')])
        self.movies = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/movies')])
        self.television = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/television')])
        self.games = ', '.join([element['name'] for element in self.graph.get(self.facebook_id + '/games')])
        self.likes = "\n".join(["%s (%s)" % (element['name'], element['category']) for element in self.graph.get(str(self.facebook_id) + '/likes')])
        self.geolocation = ','.join([str(element[1]) for element in self.graph.get(str(profile['location']['id']))['location'].items() if element[0] in ['latitude','longitude']]) if profile.has_key('location') else None
        self.save()
    
    @property
    def graph(self):
        """Return a GraphAPI instance with the user's access token."""
        try:
            from facepy import GraphAPI
            return GraphAPI(self.oauth_token.token)
        except ImportError:
            pass
            
        try:
            from facebook import GraphAPI
            return GraphAPI(self.oauth_token.token)
        except ImportError:
            pass
        
        raise ImportError('Neither Facepy nor Facebook-SDK could be imported')
        
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