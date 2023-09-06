"""
Implements a simple REST API for updating unit and course settings.

Setters:
    POST: ai_aside/v1/:course_id - (payload: { enabled: True/False })
    POST: ai_aside/v1/:course_id/:unit_id - (payload: { enabled: True/False })

Getters:
    GET: ai_aside/v1/:course_id - (response: { success: True/False, enabled: True/False })
    GET: ai_aside/v1/:course_id/:unit_id - (response: { success: True/False, enabled: True/False })

Delete:
    DELETE: ai_aside/v1/:course_id - (response: { success: True/False })
    DELETE: ai_aside/v1/:course_id/:unit_id - (response: { success: True/False })

Both GET and DELETE methods respond with a 404 if the setting cannot be found.
"""
from ai_aside.config_api.api import (
    delete_course_settings,
    delete_unit_settings,
    get_course_settings,
    get_unit_settings,
    is_summary_config_enabled,
    reset_course_unit_settings,
    set_course_settings,
    set_unit_settings,
)
from ai_aside.config_api.exceptions import AiAsideException, AiAsideNotFoundException
from ai_aside.config_api.validators import validate_course_key, validate_unit_key
from ai_aside.config_api.view_utils import AiAsideAPIView, APIResponse


class CourseSummaryConfigEnabledAPIView(AiAsideAPIView):
    """
    Simple GET endpoint to expose whether the course may use summary config.
    """
    def get(self, request, course_id=None):
        """Expose whether the course may use summary config"""
        if course_id is None:
            raise AiAsideNotFoundException

        course_key = validate_course_key(course_id)
        enabled = is_summary_config_enabled(course_key)
        return APIResponse(success=True, data={'enabled': enabled})


class CourseEnabledAPIView(AiAsideAPIView):
    """Handlers for course level settings"""
    def get(self, request, course_id=None):
        """Gets the enabled state for a course"""
        if course_id is None:
            raise AiAsideNotFoundException

        course_key = validate_course_key(course_id)
        settings = get_course_settings(course_key)
        return APIResponse(success=True, data=settings)

    def post(self, request, course_id=None):
        """Update the course and reset if its necessary"""

        # enabled: Updates the course enabled default state
        enabled = request.data.get('enabled')

        # reset: If it is present, it will delete all unit settings, resetting them back to the default
        reset = request.data.get('reset')

        try:
            course_key = validate_course_key(course_id)
            set_course_settings(course_key, {'enabled': enabled})
            if reset:
                reset_course_unit_settings(course_key)
        except TypeError as error:
            raise AiAsideException('Invalid parameters') from error

        return APIResponse(success=True)

    def delete(self, request, course_id=None):
        """Deletes the settings for a module"""

        if course_id is None:
            raise AiAsideNotFoundException

        course_key = validate_course_key(course_id)
        delete_course_settings(course_key)
        return APIResponse(success=True)


class UnitEnabledAPIView(AiAsideAPIView):
    """Handlers for module level settings"""
    def get(self, request, course_id=None, unit_id=None):
        """Gets the enabled state for a unit"""
        if course_id is None or unit_id is None:
            raise AiAsideNotFoundException

        course_key = validate_course_key(course_id)
        unit_key = validate_unit_key(unit_id)
        settings = get_unit_settings(course_key, unit_key)
        return APIResponse(success=True, data=settings)

    def post(self, request, course_id=None, unit_id=None):
        """Sets the enabled state for a unit"""

        enabled = request.data.get('enabled')

        try:
            course_key = validate_course_key(course_id)
            unit_key = validate_unit_key(unit_id)
            set_unit_settings(course_key, unit_key, {'enabled': enabled})
        except TypeError as error:
            raise AiAsideException('Invalid parameters') from error

        return APIResponse(success=True)

    def delete(self, request, course_id=None, unit_id=None):
        """Deletes the settings for a unit"""

        if course_id is None or unit_id is None:
            raise AiAsideNotFoundException

        course_key = validate_course_key(course_id)
        unit_key = validate_unit_key(unit_id)
        delete_unit_settings(course_key, unit_key,)
        return APIResponse(success=True)
