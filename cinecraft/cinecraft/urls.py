"""
URL configuration for cinecraft project.
"""
from admin_frontend.admin import admin_site
from django.urls import include, path

urlpatterns = [
    path('admin/front/', include('admin_frontend.urls')),   # endpoints for admin frontend (should be above admin/)
    path('admin/', admin_site.urls),
    path('', include('cineapp.urls')),
]
