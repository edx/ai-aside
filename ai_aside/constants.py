"""Constants for AI-Aside."""

# Regex for Course ID URL patterns
COURSE_ID_REGEX = r'[^/+]+(/|\+)[^/+]+(/|\+)[^/]+'
COURSE_ID_PATTERN = r'(?P<course_id>{})'.format(COURSE_ID_REGEX)

# Regex for Usage ID URL patterns (Unit IDs)
UNIT_ID_REGEX = r'(?:i4x://?[^/]+/[^/]+/[^/]+/[^@]+(?:@[^/]+)?)|(?:[^/]+)'
UNIT_ID_PATTERN = r'(?P<unit_id>{})'.format(UNIT_ID_REGEX)

"""
Constants used by DjangoXBlockUserService
"""

# Optional attributes stored on the XBlockUser

# The personally identifiable user ID.
ATTR_KEY_USER_ID = 'edx-platform.user_id'
# The user's role in the course ('staff', 'instructor', or 'student').
ATTR_KEY_USER_ROLE = 'edx-platform.user_role'
