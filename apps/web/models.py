from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django import forms
from django.contrib.auth.models import AbstractUser
from django.db import models

from config import settings


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        # This is required to point to the custom user model
        db_table = 'custom_user'

    # Fix the reverse accessor clash by setting a unique related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.user.username} profile'


@receiver(post_save, sender=User)
def create_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Category(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Quiz(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="quizzes")
    name = models.CharField(max_length=255)
    time_start = models.DateTimeField(default=timezone.now)
    time_end = models.DateTimeField()
    STATUS_CHOICES = (
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')

    def __str__(self):
        return self.name


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions")
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    description = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    is_active = models.BooleanField(default=True)


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="quiz_questions")
    user_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="quiz_questions")
