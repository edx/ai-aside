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
from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_aside.config_api.api import (
    NotFoundError,
    delete_course_settings,
    delete_unit_settings,
    get_course_settings,
    get_unit_settings,
    is_summary_config_enabled,
    reset_course_unit_settings,
    set_course_settings,
    set_unit_settings,
)


class APIResponse(Response):
    """API Response"""
    def __init__(self, data=None, http_status=None, content_type=None, success=False):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {'response': {'success': success}}
        reply['response'].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)


class CourseSummaryConfigEnabledAPIView(APIView):
    """
    Simple GET endpoint to expose whether the course may use summary config.
    """

    def get(self, request, course_id=None):
        """Expose whether the course may use summary config"""
        if course_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            enabled = is_summary_config_enabled(CourseKey.from_string(course_id))
            return APIResponse(success=True, data={'enabled': enabled})
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)


class CourseEnabledAPIView(APIView):
    """Handlers for course level settings"""

    def get(self, request, course_id=None):
        """Gets the enabled state for a course"""
        if course_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            settings = get_course_settings(CourseKey.from_string(course_id))
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)
        except NotFoundError:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        return APIResponse(success=True, data=settings)

    def post(self, request, course_id=None):
        """Update the course and reset if its necessary"""

        # enabled: Updates the course enabled default state
        enabled = request.data.get('enabled')

        # reset: If it is present, it will delete all unit settings, resetting them back to the default
        reset = request.data.get('reset')

        try:
            course_key = CourseKey.from_string(course_id)
            set_course_settings(course_key, {'enabled': enabled})
            if reset:
                reset_course_unit_settings(course_key)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)
        except TypeError:
            data = {'message': 'Invalid parameters'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        return APIResponse(success=True)

    def delete(self, request, course_id=None):
        """Deletes the settings for a module"""

        if course_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            delete_course_settings(CourseKey.from_string(course_id))
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)
        except NotFoundError:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        return APIResponse(success=True)


class UnitEnabledAPIView(APIView):
    """Handlers for module level settings"""

    def get(self, request, course_id=None, unit_id=None):
        """Gets the enabled state for a unit"""
        if course_id is None or unit_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            settings = get_unit_settings(
                CourseKey.from_string(course_id),
                UsageKey.from_string(unit_id),
            )
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)
        except NotFoundError:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        return APIResponse(success=True, data=settings)

    def post(self, request, course_id=None, unit_id=None):
        """Sets the enabled state for a unit"""

        enabled = request.data.get('enabled')

        try:
            set_unit_settings(
                CourseKey.from_string(course_id),
                UsageKey.from_string(unit_id),
                {'enabled': enabled})
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)
        except TypeError:
            data = {'message': 'Invalid parameters'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        return APIResponse(success=True)

    def delete(self, request, course_id=None, unit_id=None):
        """Deletes the settings for a unit"""

        if course_id is None or unit_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            delete_unit_settings(
                CourseKey.from_string(course_id),
                UsageKey.from_string(unit_id),
            )
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)
        except NotFoundError:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        return APIResponse(success=True)
