from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView
from .models import Quiz
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
# from apps.web.forms import UserRegistrationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")

# def register(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'templates/register.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff or u.has_perm('quiz.manage_quiz'))
class QuizManagementView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Quiz
    template_name = 'templates/quiz_management.html'
    permission_required = 'quiz.manage_quiz'  # Can also be a list of permissions

    # If using a custom user model with a 'staff' field
    def get_queryset(self):
        if self.request.user.is_staff:
            return Quiz.objects.all()
        # Possibly add more logic for users with specific permissions
        return Quiz.objects.filter(user=self.request.user)
