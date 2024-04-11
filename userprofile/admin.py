from django.contrib import admin
from .models import Userprofile, State

@admin.register(Userprofile)
class UserprofileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_vendor', 'company_address', 'website']
    list_filter = ['is_vendor']
    search_fields = ['user__username', 'user__email','user__first_name','user__last_name']

admin.site.register(State)
