from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Category, Question, QuizQuestion, Choice
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.utils import timezone


# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class MyLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("base")


def base(request):
    return render(request, "base.html")


class home(LoginRequiredMixin, ListView):
    model = Quiz
    template_name = 'home.html'
    context_object_name = 'quizzes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()  # Add all categories to the context
        if self.request.user.is_authenticated:
            context['user_quizzes'] = Quiz.objects.filter(user=self.request.user).order_by('-time_start')
        return context

    def get_queryset(self):
        return Quiz.objects.all().order_by('-time_start')


class QuizView(LoginRequiredMixin, View):

    def get(self, request, id):
        # make sure noly one quiz is ongoing
        ongoing_quiz = Quiz.objects.filter(user=request.user, status='ongoing').first()
        if ongoing_quiz:
            # return redirect('quiz', id=ongoing_quiz.id)
            return HttpResponseForbidden("You already have an ongoing quiz.")
        else:
            quiz = get_object_or_404(Quiz, pk=id)
            questions = QuizQuestion.objects.filter(quiz=quiz)  # Assuming QuizQuestion has a foreign key to Quiz
            return render(request, 'quiz.html', {'quiz': quiz, 'questions': questions})

    def post(self, request, id):
        quiz = get_object_or_404(Quiz, pk=id)
        # Process the submitted answers
        # iterate over the submitted answers and check them against the correct choices
        # Optionally calculate the score
        correct_count = 0
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                selected_choice = value

                try:
                    # question = QuizQuestion.objects.get(pk=question_id)
                    choice = Choice.objects.get(pk=question_id)
                    correct_choice = choice.get(is_correct=True)

                    if str(correct_choice.id) == selected_choice:
                        correct_count += 1

                except (QuizQuestion.DoesNotExist, Choice.DoesNotExist):
                    # Handle the error / log
                    pass
        quiz.time_end = timezone.now()
        quiz.status = 'completed'

        quiz.save()

        return redirect('quiz_result.html', quiz_id=quiz.id)  # Redirect to the results page or another appropriate URL
