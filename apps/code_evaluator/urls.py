from django.urls import path

from apps.code_evaluator import views

urlpatterns = [
    path('', views.index, name='index'),
]