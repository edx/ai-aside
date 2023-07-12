"""
URLs for ai_aside.
"""
from django.urls import re_path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import

from . import views

app_name = 'ai_aside'

urlpatterns = [
    re_path(r'david_is_here', views.homePageView)
]