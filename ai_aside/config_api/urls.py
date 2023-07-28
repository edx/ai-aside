"""
implements a simple REST API for updating unit and course settings
"""
from django.urls import re_path

from ai_aside.config_api.views import CourseEnabledAPIView, CourseSummaryConfigEnabledAPIView, UnitEnabledAPIView
from ai_aside.constants import COURSE_ID_PATTERN, UNIT_ID_PATTERN

urlpatterns = [
    re_path(r'^v1/{course_id}/?$'.format(
        course_id=COURSE_ID_PATTERN
    ), CourseEnabledAPIView.as_view(), name='api-course-settings'),
    re_path(r'^v1/{course_id}/configurable/?$'.format(
        course_id=COURSE_ID_PATTERN
    ), CourseSummaryConfigEnabledAPIView.as_view(), name='api-course-configurable'),
    re_path(r'^v1/{course_id}/{unit_id}/?$'.format(
        course_id=COURSE_ID_PATTERN,
        unit_id=UNIT_ID_PATTERN
    ), UnitEnabledAPIView.as_view(), name='api-unit-settings'),
]
