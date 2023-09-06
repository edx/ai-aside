"""
Implements an API for updating unit and course settings.
"""
from ai_aside.config_api.exceptions import AiAsideNotFoundException
from ai_aside.config_api.internal import _get_course, _get_course_units, _get_unit
from ai_aside.models import AIAsideCourseEnabled, AIAsideUnitEnabled
from ai_aside.waffle import summaries_configuration_enabled


def get_course_settings(course_key):
    """
    Gets the settings of a course.

    Returns: dictionary of the form:
        `{'enabled': bool}`
    """
    record = _get_course(course_key)
    fields = {
        'enabled': record.enabled
    }

    return fields


def set_course_settings(course_key, settings):
    """
    Sets the settings of a course.

    Expects: settings to be a dictionary of the form:
        `{'enabled': bool}`

    Raises AiAsideNotFoundException if the settings are not found.
    """
    enabled = settings['enabled']

    if not isinstance(enabled, bool):
        raise TypeError

    update = {'enabled': enabled}

    AIAsideCourseEnabled.objects.update_or_create(
        course_key=course_key,
        defaults=update,
    )


def delete_course_settings(course_key):
    """
    Deletes the settings of a course.

    Raises AiAsideNotFoundException if the settings are not found.
    """
    reset_course_unit_settings(course_key)
    record = _get_course(course_key)
    record.delete()


def get_unit_settings(course_key, unit_key):
    """
    Gets the settings of a unit.

    Returns: dictionary of the form:
        `{'enabled': bool}`
    """
    record = _get_unit(course_key, unit_key)

    fields = {
        'enabled': record.enabled
    }

    return fields


def reset_course_unit_settings(course_key):
    """
    Deletes the unit settings of a course.
    """
    return _get_course_units(course_key).delete()


def set_unit_settings(course_key, unit_key, settings):
    """
    Sets the settings of a course's unit.

    Expects: settings as a dictionary of the form:
        `{'enabled': bool}`

    Raises AiAsideNotFoundException if the settings are not found.
    """
    enabled = settings['enabled']

    if not isinstance(enabled, bool):
        raise TypeError

    settings = {'enabled': enabled}

    AIAsideUnitEnabled.objects.update_or_create(
        course_key=course_key,
        unit_key=unit_key,
        defaults=settings,
    )


def delete_unit_settings(course_key, unit_key):
    """
    Deletes the settings of a unit.

    Raises AiAsideNotFoundException if the settings are not found.
    """
    record = _get_unit(course_key, unit_key)
    record.delete()


def is_summary_config_enabled(course_key):
    """
    Is this course even allowed to configure summaries?

    This is just a wrapper for the waffle flag for use
    by the views.
    """
    return summaries_configuration_enabled(course_key)


def is_course_settings_present(course_key):
    """
    Exist a course for the given key?
    """
    try:
        course = _get_course(course_key)
        return course is not None
    except AiAsideNotFoundException:
        return False


def is_summary_enabled(course_key, unit_key=None):
    """
    Gets the enabled state of a course's unit.
    It considers both the state of a unit's override and a course defaults.
    """

    # If the feature flag is disabled, always returns False.
    if not summaries_configuration_enabled(course_key):
        return False

    if unit_key is not None:
        try:
            unit = _get_unit(course_key, unit_key)

            if unit is not None:
                return unit.enabled
        except AiAsideNotFoundException:
            pass

    try:
        course = _get_course(course_key)
    except AiAsideNotFoundException:
        return False

    if course is not None:
        return course.enabled

    return False
