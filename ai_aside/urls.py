"""
URLs for ai_aside.
"""
from django.urls import path, re_path  # pylint: disable=unused-import
from django.views.generic import TemplateView  # pylint: disable=unused-import

from ai_aside.config_api.urls import urlpatterns as apipatterns

app_name = 'ai_aside'

urlpatterns = []

urlpatterns += apipatterns
