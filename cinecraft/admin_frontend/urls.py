from django.urls import path

from . import views

app_name = "admin_frontend"

urlpatterns = [
    path("submission/<int:pk>/action/", views.submission_action, name="submission_action"),
    path("submission/<int:pk>/delete/", views.submission_delete, name="submission_delete"),
    path("submission/<int:pk>/edit/", views.submission_edit, name="submission_edit"),
    path("logout/", views.custom_admin_logout, name="custom_admin_logout"),
]