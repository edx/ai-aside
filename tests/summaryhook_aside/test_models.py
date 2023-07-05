"""Tests for the models"""
from django.test import TestCase
from opaque_keys.edx.keys import CourseKey, UsageKey

from ai_aside.models import AIAsideCourseEnabled, AIAsideUnitEnabled

course_keys = [
    'course-v1:edX+DemoX+Demo_Course',
    'course-v1:edX+DemoX+Demo_Course-2',
]

unit_keys = [
    "block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_0270f6de40fc",
    "block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_321ac313f2de",
]


class TestModels(TestCase):
    """Utils model tests"""

    def setUp(self):
        super().setUp()

        # Create some test cases

        # First course is disabled
        AIAsideCourseEnabled.objects.create(
            course_key=CourseKey.from_string(course_keys[0]),
            enabled=False,
        )

        # 2nd course is enabled
        AIAsideCourseEnabled.objects.create(
            course_key=CourseKey.from_string(course_keys[1]),
            enabled=True,
        )

        # 2nd course has an enabled and a disabled unit
        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_keys[1]),
            unit_key=UsageKey.from_string(unit_keys[0]),
            enabled=True,
        )

        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_keys[1]),
            unit_key=UsageKey.from_string(unit_keys[1]),
            enabled=False,
        )

    def test_course_enabled(self):
        """Check that the models work as expected."""

        self.assertEqual(AIAsideCourseEnabled.objects.count(), 2)

        self.assertFalse(AIAsideCourseEnabled.objects.filter(
            course_key=course_keys[0],
        ).first().enabled)

        self.assertTrue(AIAsideCourseEnabled.objects.filter(
            course_key=course_keys[1],
        ).first().enabled)

    def test_unit_enabled(self):
        """Check that the models work as expected."""

        self.assertEqual(AIAsideUnitEnabled.objects.count(), 2)

        self.assertTrue(AIAsideUnitEnabled.objects.filter(
            course_key=course_keys[1],
            unit_key=unit_keys[0],
        ).last().enabled)

        self.assertFalse(AIAsideUnitEnabled.objects.filter(
            course_key=course_keys[1],
            unit_key=unit_keys[1],
        ).last().enabled)
