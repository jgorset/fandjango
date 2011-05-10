from django.contrib import admin
from models import User, OAuthToken

class UserAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'facebook_id', 'authorized', 'created_at', 'last_seen_at']
    
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'issued_at', 'expires_at', 'expired']
    
admin.site.register(User, UserAdmin)
admin.site.register(OAuthToken, OAuthTokenAdmin)
