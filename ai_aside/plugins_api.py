"""
Concrete implementations of abstract methods of the CourseApp plugin ABC, for use by the AiAsideCourseApp.

Because the AiAsideCourseApp plugin inherits from the CourseApp class, which is imported from the
edx-platform, we cannot test that plugin directly, because pytest will run outside the platform context.
Instead, the CourseApp abstract methods are implemented here and
imported into and used by the AiAsideCourseApp. This way, these implementations can be tested.
"""

# pylint: disable=import-error
from lms.djangoapps.courseware.access import get_user_role

from ai_aside.config_api.api import is_summary_config_enabled, is_summary_enabled, set_course_settings


def is_available(course_key):
    """
    Return if the Xpert Unit Summaries service is available for use in the first place.

    Returns:
        bool: Availability status of Xpert Unit Summaries.
    """
    return is_summary_config_enabled(course_key)


def is_enabled(course_key):
    """
    Return a boolean indicating if this course app is enabled for a given course.

    If the app is enabled, it will show up in the UI at all for that course,
    allowing instructors to enable/disable unit summaries on the course level,
    unless the platform wide setting SUMMARY_ENABLED_BY_DEFAULT is set to False later on.

    Args:
        course_key (CourseKey): Course key for course whose unit summary enablement is being checked.

    Returns:
        bool: The status of the course app for the specified course.
    """
    return is_summary_enabled(course_key)


# pylint: disable=unused-argument
def set_enabled(course_key, enabled, user):
    """
    Update the status of this app for the provided course and return the new status.

    Args:
        course_key (CourseKey): The course key for the course for which the app should be enabled.
        enabled (bool): The new status of the app.
        user (User): The user performing this operation.

    Returns:
        bool: The new status of the course app.
    """
    settings = {'enabled': enabled}
    obj = set_course_settings(course_key, settings)

    return obj.enabled


def get_allowed_operations(course_key, user=None):
    """
    Return a dictionary of available operations for this app.

    Not all apps will support being configured, and some may support
    other operations via the UI. This will list, the minimum whether
    the app can be enabled/disabled and whether it can be configured.

    Args:
        course_key (CourseKey): The course key for a course.
        user (User): The user for which the operation is to be tested.

    Returns:
        A dictionary that has keys like 'enable', 'configure' etc
        with values indicating whether those operations are allowed.

        get_allowed_operations: function that returns a dictionary of the form
                                {'enable': <bool>, 'configure': <bool>}.
    """
    if not user:
        return {'configure': False, 'enable': False}
    else:
        user_role = get_user_role(user, course_key)
        is_staff = user_role in ('staff', 'instructor')

    return {'configure': False, 'enable': is_staff}
