from django.contrib import admin
# apps/blog/admin.py
from django.contrib import admin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Quiz, Category
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'phone']
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('phone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Profile', {'fields': ('phone',)}),
    )


class QuizAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'category', 'time_start', 'time_end']
    list_filter = ('category',)  # Filters you can use on the side of the list page
    search_fields = ('name', 'category__name')  # Fields that can be searched
    ordering = ('-time_start',)  # Default ordering
    fields = ('name', 'category', 'time_start', 'time_end')  # Fields in the form view
    readonly_fields = ('time_start', 'time_end')  # Fields that are read-only in the form view


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)

