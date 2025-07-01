from django.urls import path

from apps.analyzer import views

urlpatterns = [
    path('sql/', views.sql_analyzer, name='sql'),
    path('code/', views.code_analyzer, name='code'),
    # path('upload/', views.upload_files, name='upload_files'),
    # path('results/', views.analysis_results, name='analysis_results'),
    # path('file/<int:file_id>/', views.file_detail, name='file_detail'),
]