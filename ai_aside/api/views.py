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

from ai_aside.models import AIAsideCourseEnabled, AIAsideUnitEnabled


class APIResponse(Response):
    """API Response"""
    def __init__(self, data=None, http_status=None, content_type=None, success=False):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {'response': {'success': success}}
        reply['response'].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)


class CourseEnabledAPIView(APIView):
    """Handlers for course level settings"""

    def get(self, request, course_id=None):
        """Gets the enabled state for a course"""
        if course_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        try:
            record = AIAsideCourseEnabled.objects.get(
                course_key=course_key,
            )
        except AIAsideCourseEnabled.DoesNotExist:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        enabled = record.enabled

        data = {'enabled': enabled}
        return APIResponse(success=True, data=data)

    def post(self, request, course_id=None):
        """Sets the enabled state for a course"""

        enabled = request.data.get('enabled')

        if not isinstance(enabled, bool):
            data = {'message': 'Invalid parameters'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        if course_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        AIAsideCourseEnabled.objects.update_or_create(
            course_key=course_key,
            defaults={'enabled': enabled}
        )

        data = {'enabled': enabled}

        return APIResponse(success=True, data=data)

    def delete(self, request, course_id=None):
        """Deletes the settings for a module"""
        if course_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            course_key = CourseKey.from_string(course_id)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        try:
            AIAsideCourseEnabled.objects.get(
                course_key=course_key,
            ).delete()
        except AIAsideCourseEnabled.DoesNotExist:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        return APIResponse(success=True)


class UnitEnabledAPIView(APIView):
    """Handlers for module level settings"""
    def get(self, request, course_id=None, unit_id=None):
        """Gets the enabled state for a module"""
        if course_id is None or unit_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            course_key = CourseKey.from_string(course_id)
            unit_key = UsageKey.from_string(unit_id)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        try:
            record = AIAsideUnitEnabled.objects.get(
                course_key=course_key,
                unit_key=unit_key,
            )
        except AIAsideUnitEnabled.DoesNotExist:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        if record is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        enabled = record.enabled

        data = {'enabled': enabled}
        return APIResponse(success=True, data=data)

    def post(self, request, course_id=None, unit_id=None):

        """Sets the enabled state for a module"""
        if course_id is None or unit_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        enabled = request.data.get('enabled')

        if not isinstance(enabled, bool):
            data = {'message': 'Invalid parameters'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        try:
            course_key = CourseKey.from_string(course_id)
            unit_key = UsageKey.from_string(unit_id)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        AIAsideUnitEnabled.objects.update_or_create(
            course_key=course_key,
            unit_key=unit_key,
            defaults={'enabled': enabled}
        )

        data = {'enabled': enabled}

        return APIResponse(success=True, data=data)

    def delete(self, request, course_id=None, unit_id=None):
        """Deletes the settings for a module"""
        if course_id is None or unit_id is None:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        try:
            course_key = CourseKey.from_string(course_id)
            unit_key = UsageKey.from_string(unit_id)
        except InvalidKeyError:
            data = {'message': 'Invalid Key'}
            return APIResponse(http_status=status.HTTP_400_BAD_REQUEST, data=data)

        try:
            AIAsideUnitEnabled.objects.get(
                course_key=course_key,
                unit_key=unit_key,
            ).delete()
        except AIAsideUnitEnabled.DoesNotExist:
            return APIResponse(http_status=status.HTTP_404_NOT_FOUND)

        return APIResponse(success=True)
