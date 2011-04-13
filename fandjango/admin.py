from django.contrib import admin
from models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'facebook_id', 'created_at', 'last_seen_at']
    
admin.site.register(User, UserAdmin)
