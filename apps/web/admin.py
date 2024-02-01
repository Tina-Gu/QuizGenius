from django.contrib import admin
# apps/blog/admin.py
from django.contrib import admin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Quiz, Category, Question, QuizQuestion, Choice
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class QuizInline(admin.TabularInline):
    model = Quiz


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # How many empty forms to display


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1  # How many extra fo


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
    # inlines = [QuizInline]


class QuizAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'category', 'time_start', 'time_end']
    list_filter = ['category',]
    search_fields = ['name', 'category']
    ordering = ['-time_start',]
    fields = ['name', 'category', 'time_start', 'time_end']
    # readonly_fields = ['time_start', 'time_end']
    inlines = [QuizQuestionInline]

    def save_model(self, request, obj, form, change):
        if not obj.user_id:
            obj.user = request.user
        super().save_model(request, obj, form, change)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['category', 'description', 'is_active']
    search_fields = ['is_active', ]  # Fields that can be searched
    list_filter = ['category']
    fields = ['category', 'description', 'is_active']  # Fields in the form view
    inlines = [ChoiceInline]


class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question', 'user_choice']
    list_filter = ['quiz', 'question', 'user_choice']
    search_fields = ['quiz__name', 'question__description']


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'description', 'is_correct']
    list_filter = ['question', 'is_correct']
    search_fields = ['description']


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizQuestion, QuizQuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
