from django.contrib import admin
# apps/blog/admin.py
from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)


# admin.site.unregister(User)
admin.site.register(User, UserAdmin)
# Register your models here.
