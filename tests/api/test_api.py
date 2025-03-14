"""
Tests for the API
"""
from unittest.mock import patch

from django.test import TestCase, override_settings
from opaque_keys.edx.keys import CourseKey, UsageKey

from ai_aside.config_api.api import (
    delete_course_settings,
    delete_unit_settings,
    get_course_settings,
    get_unit_settings,
    is_course_settings_present,
    is_summary_enabled,
    reset_course_unit_settings,
    set_course_settings,
    set_unit_settings,
)
from ai_aside.config_api.exceptions import AiAsideNotFoundException
from ai_aside.models import AIAsideCourseEnabled, AIAsideUnitEnabled

course_keys = [
    CourseKey.from_string('course-v1:edX+DemoX+Demo_Course'),
    CourseKey.from_string('course-v1:edX+DemoX+Demo_Course-2'),
    CourseKey.from_string('course-v1:edX+DemoX+Demo_Course-3'),
]

unit_keys = [
    UsageKey.from_string('block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_0270f6de40fc'),
    UsageKey.from_string('block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_321ac313f2de'),
    UsageKey.from_string('block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_12b22cfd23e2'),
]


@override_settings(SUMMARY_ENABLED_BY_DEFAULT=False)
class TestApiMethods(TestCase):
    """API Endpoint Method tests"""
    def test_set_course_settings(self):
        course_key = course_keys[0]

        set_course_settings(course_key, {'enabled': True})

        res = AIAsideCourseEnabled.objects.filter(course_key=course_key)

        self.assertEqual(res.count(), 1)
        self.assertTrue(res.get().enabled)

    def test_set_course_settings_duplicates(self):
        course_key = course_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key,
            enabled=True
        )

        set_course_settings(course_key, {'enabled': False})

        res = AIAsideCourseEnabled.objects.filter(course_key=course_key)

        self.assertEqual(res.count(), 1)
        self.assertFalse(res.get().enabled)

    def test_set_course_settings_invalid_parameters(self):
        course_key = course_keys[0]

        with self.assertRaises(TypeError):
            set_course_settings(course_key, {'enabled': 'false'})

        res = AIAsideCourseEnabled.objects.filter(course_key=course_key)

        self.assertEqual(res.count(), 0)

    def test_get_course_settings(self):
        course_key = course_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key,
            enabled=True
        )

        settings = get_course_settings(course_key)

        self.assertTrue(settings['enabled'])

    def test_get_course_settings_not_found(self):
        with self.assertRaises(AiAsideNotFoundException):
            get_course_settings(course_keys[1])

    def test_course_delete(self):
        course_key = course_keys[0]
        unit_key = unit_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key,
            enabled=True
        )

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key,
            enabled=True
        )

        delete_course_settings(course_key)

        courses = AIAsideCourseEnabled.objects.filter(course_key=course_key)
        units = AIAsideUnitEnabled.objects.filter(course_key=course_key)

        self.assertEqual(courses.count(), 0)
        self.assertEqual(units.count(), 0)

    def test_course_delete_not_found(self):
        with self.assertRaises(AiAsideNotFoundException):
            delete_course_settings(course_keys[1])

    def test_course_delete_not_found_reset_all_units(self):
        course_key = course_keys[1]
        unit_key = unit_keys[1]

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key,
        )

        units = AIAsideUnitEnabled.objects.filter(course_key=course_key)

        with self.assertRaises(AiAsideNotFoundException):
            self.assertEqual(units.count(), 1)
            delete_course_settings(course_keys[1])
            self.assertEqual(units.count(), 0)

    def test_set_unit_settings(self):
        course_key = course_keys[0]
        unit_key = unit_keys[0]

        set_unit_settings(course_key, unit_key, {'enabled': True})

        res = AIAsideUnitEnabled.objects.filter(
            course_key=course_key,
            unit_key=unit_key,
        )

        self.assertEqual(res.count(), 1)
        self.assertTrue(res.get().enabled)

    def test_set_unit_settings_check_duplicates(self):
        course_key = course_keys[0]
        unit_key = unit_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key,
            enabled=True,
        )

        set_unit_settings(course_key, unit_key, {'enabled': False})

        res = AIAsideUnitEnabled.objects.filter(
            course_key=course_key,
            unit_key=unit_key,
        )

        self.assertEqual(res.count(), 1)
        self.assertFalse(res.get().enabled)

    def test_set_unit_settings_invalid_parameters(self):
        course_key = course_keys[0]
        unit_key = unit_keys[0]

        with self.assertRaises(TypeError):
            set_unit_settings(course_key, unit_key, {'enabled': 'false'})

        res = AIAsideUnitEnabled.objects.filter(
            course_key=course_key,
            unit_key=unit_key,
        )

        self.assertEqual(res.count(), 0)

    def test_get_unit_settings(self):
        course_key = course_keys[0]
        unit_key = unit_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key,
            enabled=True,
        )

        settings = get_unit_settings(course_key, unit_key)

        self.assertTrue(settings['enabled'])

    def test_get_unit_settings_not_found(self):
        course_key = course_keys[1]
        unit_key = unit_keys[1]

        with self.assertRaises(AiAsideNotFoundException):
            get_unit_settings(course_key, unit_key)

    def test_unit_delete(self):
        course_key = course_keys[0]
        unit_key = unit_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key,
            enabled=True,
        )

        delete_unit_settings(course_key, unit_key)

        res = AIAsideUnitEnabled.objects.filter(
            course_key=course_key,
            unit_key=unit_key,
            enabled=True,
        )

        self.assertEqual(res.count(), 0)

    def test_unit_delete_not_found(self):
        course_key = course_keys[1]
        unit_key = unit_keys[1]

        with self.assertRaises(AiAsideNotFoundException):
            delete_unit_settings(course_key, unit_key)

    @patch('ai_aside.config_api.api.summaries_configuration_enabled')
    def test_is_summary_enabled_course(self, mock_enabled):
        mock_enabled.return_value = True
        course_key_true = course_keys[0]
        course_key_false = course_keys[1]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key_true,
            enabled=True,
        )
        AIAsideCourseEnabled.objects.create(
            course_key=course_key_false,
            enabled=False,
        )

        self.assertTrue(is_summary_enabled(course_key_true))
        self.assertFalse(is_summary_enabled(course_key_false))

        course_key_non_existent = course_keys[2]
        self.assertFalse(is_summary_enabled(course_key_non_existent))

    @patch('ai_aside.config_api.api.summaries_configuration_enabled')
    def test_is_summary_enabled_unit(self, mock_enabled):
        mock_enabled.return_value = True
        course_key = course_keys[0]
        unit_key_true = unit_keys[0]
        unit_key_false = unit_keys[1]

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key_true,
            enabled=True,
        )
        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_key_false,
            enabled=False,
        )

        self.assertTrue(is_summary_enabled(course_key, unit_key_true))
        self.assertFalse(is_summary_enabled(course_key, unit_key_false))

        unit_key_non_existent = unit_keys[2]
        self.assertFalse(is_summary_enabled(course_key, unit_key_non_existent))

    @patch('ai_aside.config_api.api.summaries_configuration_enabled')
    def test_is_summary_enabled_fallback(self, mock_enabled):
        mock_enabled.return_value = True
        course_key_true = course_keys[0]
        course_key_false = course_keys[1]
        course_key_non_existent = course_keys[2]
        unit_key_non_existent = unit_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key_true,
            enabled=True,
        )
        AIAsideCourseEnabled.objects.create(
            course_key=course_key_false,
            enabled=False,
        )

        self.assertTrue(is_summary_enabled(course_key_true, unit_key_non_existent))
        self.assertFalse(is_summary_enabled(course_key_false, unit_key_non_existent))
        self.assertFalse(is_summary_enabled(course_key_non_existent, unit_key_non_existent))

    def test_is_summary_enabled_disabled_feature_flag_default_false(self):
        course_key_true = course_keys[0]
        course_key_false = course_keys[1]
        course_key_non_existent = course_keys[2]
        unit_key_non_existent = unit_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key_true,
            enabled=True,
        )
        AIAsideCourseEnabled.objects.create(
            course_key=course_key_false,
            enabled=False,
        )

        self.assertFalse(is_summary_enabled(course_key_non_existent))
        self.assertFalse(is_summary_enabled(course_key_true))
        self.assertFalse(is_summary_enabled(course_key_false))
        self.assertFalse(is_summary_enabled(course_key_true, unit_key_non_existent))
        self.assertFalse(is_summary_enabled(course_key_false, unit_key_non_existent))
        self.assertFalse(is_summary_enabled(course_key_non_existent, unit_key_non_existent))

    @override_settings(SUMMARY_ENABLED_BY_DEFAULT=True)
    @patch('ai_aside.config_api.api.summaries_configuration_enabled')
    def test_is_summary_enabled_disabled_feature_flag_default_true(self, mock_enabled):
        mock_enabled.return_value = True
        course_key_true = course_keys[0]
        course_key_false = course_keys[1]
        course_key_non_existent = course_keys[2]
        unit_key_non_existent = unit_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=course_key_true,
            enabled=True,
        )
        AIAsideCourseEnabled.objects.create(
            course_key=course_key_false,
            enabled=False,
        )

        self.assertTrue(is_summary_enabled(course_key_non_existent))
        self.assertTrue(is_summary_enabled(course_key_true))
        self.assertFalse(is_summary_enabled(course_key_false))
        self.assertTrue(is_summary_enabled(course_key_true, unit_key_non_existent))
        self.assertFalse(is_summary_enabled(course_key_false, unit_key_non_existent))
        self.assertTrue(is_summary_enabled(course_key_non_existent, unit_key_non_existent))

    def test_reset_course_unit_settings(self):
        course_key = course_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_keys[0],
            enabled=True
        )

        AIAsideUnitEnabled.objects.create(
            course_key=course_key,
            unit_key=unit_keys[1],
            enabled=False
        )

        units = AIAsideUnitEnabled.objects.filter(course_key=course_key)
        self.assertEqual(units.count(), 2)

        reset_course_unit_settings(course_key)
        self.assertEqual(units.count(), 0)

    def test_is_course_settings_present(self):
        course_key = course_keys[0]

        self.assertFalse(is_course_settings_present(course_key))

        AIAsideCourseEnabled.objects.create(
            course_key=course_key,
            enabled=True,
        )

        self.assertTrue(is_course_settings_present(course_key))
