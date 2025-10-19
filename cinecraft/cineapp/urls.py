from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('otp/request/', views.request_otp_view, name='request_otp'),
    path('otp/verify/', views.verify_otp_view, name='verify_otp'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('form/<str:department_name>/', views.dynamic_form, name='dynamic_form'),
    path('success/<str:application_id>/', views.success_page, name='success_page'),
]
