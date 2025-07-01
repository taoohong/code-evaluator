from django.urls import path

from apps.code_evaluator import views

urlpatterns = [
    path('index/', views.index, name='index'),
]