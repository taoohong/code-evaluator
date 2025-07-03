from django.urls import path

from apps.analyzer import views

urlpatterns = [
    path("upload/code/", views.upload_code, name="upload_code"),
    path("upload/sql/", views.upload_sql, name="upload_sql"),
    path("upload/project/", views.upload_project, name="upload_project"),
    # path("results/", views.analysis_results, name="results"),
]
