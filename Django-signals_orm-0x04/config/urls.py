"""
URL configuration for Django-signals_orm-0x04 project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('messaging/', include('messaging.urls')),
]
