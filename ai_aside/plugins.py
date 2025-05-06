"""
Plugins for the Xpert Unit Summary application.
"""

# pylint: disable=import-error
from openedx.core.djangoapps.course_apps.plugins import CourseApp

from ai_aside import plugins_api


class AiAsideCourseApp(CourseApp):
    """
    A CourseApp plugin representing the Xpert Unit Summary feature.

    Please see the associated ADR for more details.
    """

    @classmethod
    def is_available(cls, course_key):  # pylint: disable=unused-argument
        """
        Return a boolean indicating this course app's availability for a given course.

        If an app is not available, it will not show up in the UI at all for that course,
        and it will not be possible to enable/disable/configure it.

        Args:
            course_key (CourseKey): Course key for course whose availability is being checked.

        Returns:
            bool: Availability status of app.
        """
        return plugins_api.is_available(course_key)

    @classmethod
    def is_enabled(cls, course_key):
        """
        Return if this course app is enabled for the provided course.

        Args:
            course_key (CourseKey): The course key for the course you
                want to check the status of.

        Returns:
            bool: The status of the course app for the specified course.
        """
        return plugins_api.is_enabled(course_key)

    @classmethod
    def set_enabled(cls, course_key, enabled, user):
        """
        Update the status of this app for the provided course and return the new status.

        Args:
            course_key (CourseKey): The course key for the course for which the app should be enabled.
            enabled (bool): The new status of the app.
            user (User): The user performing this operation.

        Returns:
            bool: The new status of the course app.
        """
        return plugins_api.set_enabled(course_key, enabled, user)

    @classmethod
    def get_allowed_operations(cls, course_key, user=None):
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
        return plugins_api.get_allowed_operations(course_key, user)
