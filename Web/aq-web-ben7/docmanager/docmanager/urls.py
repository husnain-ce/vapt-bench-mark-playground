"""
URL configuration for docmanager project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("docs.urls")),
]
