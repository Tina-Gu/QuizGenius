from django.urls import reverse
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

    def get_full_name(self) -> str:
        return self.first_name + self.last_name


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quizzes_user")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="quizzes_cat")
    name = models.CharField(max_length=255)
    time_start = models.DateTimeField(default=timezone.now)
    time_end = models.DateTimeField(null=True, blank=True)
    STATUS_CHOICES = (
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')

    def __str__(self):
        return self.name

    def calculate_duration(self):
        if self.time_end:
            return self.time_end - self.time_start
        else:
            # If the quiz is still ongoing, calculate duration up to the current time
            return timezone.now() - self.time_start

    def get_score(self):
        correct_answers_count = self.quiz_questions_quiz.filter(user_choice__is_correct=True).count()
        return correct_answers_count

    def get_result(self):
        score = self.get_score()
        return 'Passed' if score >= 3 else 'Failed'

    def get_user_name(self):
        user = CustomUser.objects.get(pk=self.id)
        full_name = user.get_full_name()
        print(full_name, user)
        return full_name


class Question(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions_cat")
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def get_correct_answer(self):
        return self.choices_que.filter(is_correct=True).first()

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return reverse('question_detail', kwargs={'pk': self.pk})


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices_que")
    description = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    is_active = models.BooleanField(default=True)


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="quiz_questions_quiz")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="quiz_questions_ques")
    user_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name="quiz_questions_user_choice",null=True, blank=True)
