from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.urls import reverse_lazy
from django import forms
from .models import CustomUser, Quiz, Category, Question, QuizQuestion, Choice
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    phone = forms.CharField(required=True)

    class Meta(UserCreationForm):
        model = CustomUser
        # fields = UserCreationForm.Meta.fields + ("phone",)
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'phone')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['user', 'name', 'category', 'time_start', 'time_end']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_active']


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['category', 'description', 'is_active']


class ChoiceForm(forms.ModelForm):
    DELETE = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput())

    class Meta:
        model = Choice
        fields = ['description', 'is_correct', 'is_active', 'DELETE']
        labels = {
            'description': 'Choice',
            'is_correct': 'Correct Answer',
            'DELETE': 'Delete',
        }
        widgets = {
            'is_correct': forms.RadioSelect(),
        }



