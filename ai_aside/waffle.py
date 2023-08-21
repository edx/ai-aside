"""
Waffle flag controlling summary hook distribution.

Xblocks do not generally use waffle flags,
import at use time method taken from the LTI Xblock
"""

# Namespace
WAFFLE_NAMESPACE = 'summaryhook'


# .. toggle_name: summaryhook.staff_only
# .. toggle_implementation: CourseWaffleFlag
# .. toggle_default: False
# .. toggle_description: Enables OpenAI driven summary xblock aside for staff only
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2023-03-14
# .. toggle_target_removal_date: 2023-12-06
# .. toggle_tickets: ACADEMIC-15709 (2U)
# .. toggle_warning: None.
SUMMARYHOOK_STAFF_ONLY = 'summaryhook_staff_only'


# .. toggle_name: summaryhook.summaries_configuration
# .. toggle_implementation: CourseWaffleFlag
# .. toggle_default: False
# .. toggle_description: Enables summaries configuration for course and/or unit
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2023-07-24
# .. toggle_target_removal_date: 2024-04-06
# .. toggle_tickets: ACADEMIC-16209 (2U)
# .. toggle_warning: None.
SUMMARYHOOK_SUMMARIES_CONFIGURATION = 'summaryhook_summaries_configuration'


def _is_summaryhook_waffle_flag_enabled(flag_name, course_key):
    """
    Import and return Waffle flag for enabling the summary hook.
    """
    # pylint: disable=import-outside-toplevel
    try:
        from openedx.core.djangoapps.waffle_utils import CourseWaffleFlag
        return CourseWaffleFlag(f'{WAFFLE_NAMESPACE}.{flag_name}', __name__).is_enabled(course_key)
    except ImportError:
        return False


def summary_staff_only(course_key):
    """
    Return whether the summaryhook.summaryhook_staff_only WaffleFlag is on.
    """
    return _is_summaryhook_waffle_flag_enabled(SUMMARYHOOK_STAFF_ONLY, course_key)


def summaries_configuration_enabled(course_key):
    """
    Return whether the summaryhook.summaryhook_summaries_configuration WaffleFlag is on.
    """
    return _is_summaryhook_waffle_flag_enabled(SUMMARYHOOK_SUMMARIES_CONFIGURATION, course_key)
