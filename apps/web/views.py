import random
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Quiz, Category, Question, QuizQuestion, Choice
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.views.generic.edit import UpdateView
from .forms import *
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.forms.models import inlineformset_factory


# Create your views here.
User = get_user_model()
user = User.objects.get(username='user02')
print(user.get_all_permissions())

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


class MyLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True
    def get_success_url(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse_lazy("user_management")
        else:
            return reverse_lazy("home")


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


class QuizStartView(LoginRequiredMixin, View):
    def get(self, request, category_name):
        category = get_object_or_404(Category, name=category_name)
        ongoing_quiz = Quiz.objects.filter(user=request.user, status='ongoing').first()

        if ongoing_quiz:
            return redirect('quiz', category_name=category_name, quiz_id=ongoing_quiz.id)
        else:
            try:
                quiz = Quiz.objects.create(
                    user=request.user,
                    category=category,
                    name=f"{category.name} Quiz",
                    time_start=timezone.now()
                )
                # Select 5 random questions from the category
                questions = list(Question.objects.filter(category=category, is_active=True))
                random_questions = random.sample(questions, min(5, len(questions)))

                for question in random_questions:
                    QuizQuestion.objects.create(quiz=quiz, question=question)
            except:
                return HttpResponse(status=500)

            return redirect('quiz', category_name=category_name, quiz_id=quiz.id)


class QuizView(LoginRequiredMixin, View):
    template_name = "quiz.html"

    def get(self, request, category_name, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        quiz_questions = QuizQuestion.objects.filter(quiz=quiz)
        if not quiz_questions: # eadge case, if code has error before question generator works
            category = get_object_or_404(Category, name=category_name)
            questions = list(Question.objects.filter(category=category.id, is_active=True))
            random_questions = random.sample(questions, min(5, len(questions)))
            for question in random_questions:
                QuizQuestion.objects.create(quiz=quiz, question=question)
            quiz_questions = QuizQuestion.objects.filter(quiz=quiz)
        questions_with_choices = []

        for qq in quiz_questions:
            choices = Choice.objects.filter(question=qq.question).all()
            questions_with_choices.append({
                'id': qq.question.id,
                'description': qq.question,
                'choices': [{'id': choice.id, 'description': choice.description} for choice in choices]
            })
        return render(request, self.template_name, {'quiz': quiz, 'questions': questions_with_choices})

    def post(self, request, category_name, quiz_id):
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        # Process the submitted answers
        # iterate over the submitted answers and check them against the correct choices

        for key, value in request.POST.items():
            print(key,value)
            if key.startswith('question_'):
                question_id = key.split('_')[1]
                selected_choice_id = value

                try:
                    quiz_question = QuizQuestion.objects.get(quiz=quiz, question_id=question_id)
                    # Retrieve the Choice instance using the selected choice ID from the POST data
                    selected_choice = Choice.objects.get(id=selected_choice_id)
                    # Assign the Choice instance to user_choice of the QuizQuestion
                    quiz_question.user_choice = selected_choice
                    quiz_question.save()

                    # correct_choice = quiz_question.question.get_correct_answer()

                except (QuizQuestion.DoesNotExist, Choice.DoesNotExist) as e:
                    print(e)
        quiz.time_end = timezone.now()
        quiz.status = 'completed'
        quiz.save()

        # request.session['correct_count'] = correct_count
        # request.session['category_name'] = category_name
        return redirect('quiz_result', pk=quiz.id)  # Redirect to the results page or another appropriate URL


class QuizResultView(LoginRequiredMixin, DetailView):
    model = Quiz
    template_name = 'quiz_result.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = context['quiz']
        duration = quiz.time_end - quiz.time_start
        quiz_questions = QuizQuestion.objects.filter(quiz=quiz)
        correct_count = quiz_questions.filter(user_choice__is_correct=True).count()

        context['score'] = round(quiz.get_score() / 5, 2) * 100
        context['category'] = quiz.category
        context['passed'] = quiz.get_result()

        context['results'] = [
            {
                'question': qq.question.description,
                'selected_choice': qq.user_choice.description if qq.user_choice else None,
                'correct_choice': qq.question.get_correct_answer().description,
                'all_choices': [choice.description for choice in qq.question.choices_que.all()]
            }
            for qq in quiz_questions
        ]
        return context



class UserListView(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    permission_required = 'web.view_question'
    model = User
    template_name = 'user_management/user_management.html'
    context_object_name = 'users'
    paginate_by = 5

    # def test_func(self):
    #     user = self.request.user
    #     # User must be a superuser or staff, or must have any specific permission
    #     return user.is_superuser or user.is_staff or user.has_perm('web.change_profile')

    def get_queryset(self):
        return User.objects.annotate(quiz_count=Count('quizzes_user'))

    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.is_active = not user.is_active
        user.save()
        return redirect('user_management')


class UserQuizListView(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    permission_required = 'web.view_quiz'
    model = Quiz
    template_name = 'user_management/user_quiz_management.html'
    context_object_name = 'quizzes'
    ordering = ['-time_start']

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        user_filter = self.request.GET.get('user_id')
        print(user_filter)
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            if user_filter:
                queryset = queryset.filter(user__id=user_filter)
            # If user is staff or superuser and no 'user_id' parameter, show all quizzes
            category_filter = self.request.GET.get('category')
            if category_filter:
                queryset = queryset.filter(category__name=category_filter)

        return queryset


class UserQuestionListView(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    permission_required = 'web.view_quizquestion'
    model = Question
    template_name = 'user_management/question_management.html'
    context_object_name = 'questions'

    def post(self, request, *args, **kwargs):
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, pk=question_id)

        if 'toggle_active' in request.POST:
            question.is_active = not question.is_active
            question.save()
        return redirect('question_management')


class QuestionDetailListView(LoginRequiredMixin,PermissionRequiredMixin,DetailView):
    permission_required = 'web.view_questiondetail'
    model = Question
    template_name = 'user_management/question_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['choices'] = self.object.choices_que.all()  # Assuming related_name='choices_que' in Choice model
        return context

class QuestionEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'web.change_question'
    model = Question
    form_class = QuestionForm
    template_name = 'user_management/question_edit.html'
    success_url = reverse_lazy('question_management')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = self.ChoiceFormSet(self.request.POST, instance=self.object)
        else:
            context['formset'] = self.ChoiceFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']
        if formset.is_valid():

            self.object = form.save()  # Save the Question

            # Iterate over the forms in the formset to save each choice
            for form in formset:
                choice = form.save(commit=False)
                # Set the correct answer based on a radio button or another method
                if form.cleaned_data.get('is_correct'):
                    # Unset the previous correct answer
                    Choice.objects.filter(question=self.object, is_correct=True).update(is_correct=False)
                    # Set the new correct answer
                    choice.is_correct = True
                choice.question = self.object
                choice.save()
            formset.save_m2m()  # Save many-to-many data for the formset
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

    @property
    def ChoiceFormSet(self):
        # This property will now ensure the inline formset uses ChoiceForm
        return inlineformset_factory(Question, Choice, form=ChoiceForm, extra=1, can_delete=True)


    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #
    #     new_description = request.POST.get('question_description', '')
    #     if new_description:
    #         self.object.description = new_description
    #         self.object.save()
    #
    #     # Now handle the choices and correct answer
    #     for choice in self.object.choices_que.all():
    #         choice_description = request.POST.get(f'choice_{choice.id}')
    #         correct_field = request.POST.get(f'correct_{choice.id}', '') == 'correct'
    #         correct_choice_id = request.POST.get('correct_answer')
    #         if choice_description:
    #             choice.description = choice_description
    #             choice.is_correct = str(choice.id) == correct_choice_id  # Update is_correct based on the checkbox
    #             choice.save()
    #     return redirect('question_management')
    #


class QuestionAddView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'web.add_question'
    model = Question
    form_class = QuestionForm
    template_name = 'user_management/question_add.html'
    success_url = reverse_lazy('question_management')

    ChoiceFormSet = inlineformset_factory(
        Question,
        Choice,
        fields=('description', 'is_correct'),
        extra=3,  # Specify how many choice forms want to present
        can_delete=True
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['choices_formset'] = self.ChoiceFormSet(self.request.POST)
        else:
            context['choices_formset'] = self.ChoiceFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        choices_formset = context['choices_formset']
        if choices_formset.is_valid():
            self.object = form.save()  # Save the question first
            choices_formset.instance = self.object  # Link formset to question
            choices_formset.save()  # Save the choices
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))
