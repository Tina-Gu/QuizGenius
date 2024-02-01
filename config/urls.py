"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.web.views import *
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", MyLoginView.as_view(template_name='registration/login.html'), name="login"),
    path("home/", home.as_view(), name="home"),
    path("login/", MyLoginView.as_view(template_name='registration/login.html'), name="login"),
    path("signup/", SignUpView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('category/<str:category_name>/quizzes/<int:quiz_id>', QuizView.as_view(), name='quiz'),
    path('category/<str:category_name>/start', QuizStartView.as_view(), name='quiz'),
    path('result/<int:pk>/', QuizResultView.as_view(), name='quiz_result'),
    path('user_management/', UserListView.as_view(), name='user_management'),
    path('user_quiz_management/', UserQuizListView.as_view(), name='user_quiz_management'),
    path('question_management/', UserQuestionListView.as_view(), name='question_management'),
    path('question_detail/<int:pk>', QuestionDetailListView.as_view(), name='question_detail'),
    path('question_detail/<int:pk>/edit', QuestionEditView.as_view(), name='question_edit'),
    path('question_detail/add/', QuestionAddView.as_view(), name='question_add'),
]
