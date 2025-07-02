from django.urls import path

from apps.code_evaluator import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sql/", views.sql_analyzer, name="sql"),
    path("code/", views.code_analyzer, name="code"),
]
