# Quiz Genius
## Overview
Quiz Genius is a Django-based web application designed for users to take quizzes and view their results. Leveraging Django's ORM, MVT design pattern, built-in authentication, and class-based views, this project offers a comprehensive quiz platform.

## Features

**Quiz Taking:** Users can take quizzes with multiple-choice questions.

**Results Viewing:** After completing quizzes, users can view their results.

**User Authentication:** Built-in Django authentication for user management.

**Admin Interface:** Staff members can manage quizzes, questions, categories, and user roles.

**Responsive Design:** Utilizes Bootstrap for a polished, mobile-friendly interface.

## Installation
Intstall needed requirement by using pip or docker
```
# pip
$ pip install -r requirements.txt

# docker
docker build -t QuizGenius .
$ docker-compose up
```
Migrate the database
```
$ python manage.py migrate
```
Run Server
```
$ python manage.py runserver
```

## Usage
**Registration and Login:** Users must register and log in to take quizzes.

**Taking Quizzes:** Accessible from the homepage, users can select and take quizzes.

**Viewing Results:** Users can view detailed results of their quizzes.

**Admin Functions:** Admins can add, edit, or delete quizzes, questions, and categories through the Django admin page.







