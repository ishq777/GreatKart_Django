from django.contrib import admin
from .models import Account, UserProfile
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

# Register your model here.

class AccountAdmin(UserAdmin):
     list_display = ("email", "first_name", 'last_name', 'username', 'last_login')
     
     list_display_links = ("email", 'first_name')

     readonly_fields = ['last_login']


     filter_horizontal = ()
     list_filter = ()
     fieldsets = ()


class UserProfileAdmin(admin.ModelAdmin):

     def thumbnail(self,obj):
          return format_html('<img src="{}" width="30" style="border-radius:50%;>"', obj.profile_picture.url)
     
     thumbnail.short_description = 'Profile Picture'
     list_display = ['user', 'city', 'thumbnail']


admin.site.register(Account, AccountAdmin)

admin.site.register(UserProfile, UserProfileAdmin)