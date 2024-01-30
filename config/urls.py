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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', base, name='base'),
    path("", home.as_view(), name="home"),
    path("login/", MyLoginView.as_view(template_name='login.html'), name="login"),
    path("signup/", SignUpView.as_view(), name="register"),
    path("home/", home.as_view(), name="home"),
    path('quiz/<int:id>/', QuizView.as_view(), name='quiz'),


    # path('register/', views.register(), name='register'),
]
