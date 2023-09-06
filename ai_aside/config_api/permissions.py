""" Permissions for ai-aside API"""

from rest_framework.permissions import BasePermission

from ai_aside.config_api.validators import validate_course_key
from ai_aside.platform_imports import can_change_summaries_settings


class HasStudioWriteAccess(BasePermission):
    """
    Check if the user has studio write access to a course.
    """
    def has_permission(self, request, view):
        """
        Check permissions for this class.
        """

        if not request.user.is_authenticated:
            return False

        if not request.user.is_active:
            return False

        course_key_string = view.kwargs.get('course_id')
        course_key = validate_course_key(course_key_string)

        return can_change_summaries_settings(request.user, course_key)
