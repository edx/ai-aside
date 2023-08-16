"""
Internal methods for the API.
"""
from ai_aside.models import AIAsideCourseEnabled, AIAsideUnitEnabled


class NotFoundError(Exception):
    "Raised when the course/unit is not found in the database"


def _get_course(course_key):
    "Private method that gets a course based on an id"
    try:
        record = AIAsideCourseEnabled.objects.get(
            course_key=course_key,
        )
    except AIAsideCourseEnabled.DoesNotExist as exc:
        raise NotFoundError from exc

    return record


def _get_unit(course_key, unit_key):
    "Private method that gets a unit based on an id"
    try:
        record = AIAsideUnitEnabled.objects.get(
            course_key=course_key,
            unit_key=unit_key,
        )
    except AIAsideUnitEnabled.DoesNotExist as exc:
        raise NotFoundError from exc

    return record


def _get_course_units(course_key):
    "Private method that gets a unit based on a course_key"
    return AIAsideUnitEnabled.objects.filter(
        course_key=course_key,
    )
