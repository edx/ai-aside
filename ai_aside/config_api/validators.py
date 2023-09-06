"""
Utilities related to API views
"""

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey, UsageKey

from ai_aside.config_api.exceptions import AiAsideException


def validate_course_key(course_key_string: str) -> CourseKey:
    """
    Validate and parse a course_key string, if supported.
    """
    try:
        course_key = CourseKey.from_string(course_key_string)
    except InvalidKeyError as error:
        raise AiAsideException(f"{course_key_string} is not a valid CourseKey") from error
    if course_key.deprecated:
        raise AiAsideException("Deprecated CourseKeys (Org/Course/Run) are not supported.")
    return course_key


def validate_unit_key(unit_key_string: str) -> UsageKey:
    """
    Validate and parse a unit_key string, if supported.
    """
    try:
        usage_key = UsageKey.from_string(unit_key_string)
    except InvalidKeyError as error:
        raise AiAsideException(f"{unit_key_string} is not a valid UsageKey") from error
    return usage_key
