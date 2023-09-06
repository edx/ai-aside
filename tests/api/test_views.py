"""
Tests for the API
"""
from unittest.mock import Mock, patch

import ddt
from django.urls import reverse
from opaque_keys.edx.keys import CourseKey, UsageKey

from ai_aside.models import AIAsideCourseEnabled, AIAsideUnitEnabled
from test_utils import AIAsideAPITestCase

course_keys = [
    'course-v1:edX+DemoX+Demo_Course',
    'course-v1:edX+DemoX+Demo_Course-2',
]

unit_keys = [
    'block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_0270f6de40fc',
    'block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_321ac313f2de',
]

can_change_summaries_settings = Mock()


@ddt.ddt
class TestApiViewsWithPermissions(AIAsideAPITestCase):
    """API Endpoint View tests with permissions"""
    def setUp(self):
        super().setUp()
        can_change_summaries_settings.return_value = True
        self.access_mock = patch('ai_aside.platform_imports.can_change_summaries_settings',
                                 can_change_summaries_settings)
        self.access_mock.start()

    def tearDown(self):
        super().tearDown()
        self.access_mock.stop()

    @ddt.data(True, False)
    @patch('ai_aside.config_api.api.summaries_configuration_enabled')
    def test_course_configurable(self, enabled, mock_enabled):
        mock_enabled.return_value = enabled
        course_id = course_keys[0]

        api_url = reverse('api-course-configurable', kwargs={'course_id': course_id})
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)
        self.assertEqual(response.data['response']['enabled'], enabled)

    def test_course_enabled_setter_enable_valid(self):
        course_id = course_keys[0]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.post(api_url, {'enabled': True}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)

        res = AIAsideCourseEnabled.objects.filter(course_key=course_id)

        self.assertEqual(res.count(), 1)
        self.assertTrue(res.get().enabled)

    def test_course_enabled_setter_disable_valid_and_check_duplicates(self):
        course_id = course_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            enabled=True,
        )

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.post(api_url, {'enabled': False}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)

        res = AIAsideCourseEnabled.objects.filter(course_key=course_id)

        self.assertEqual(res.count(), 1)
        self.assertFalse(res.get().enabled)

    def test_course_enabled_setter_invalid_parameters(self):
        course_id = course_keys[0]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.post(api_url, {'enabled': 'true'}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['response']['message'], 'Invalid parameters')

        res = AIAsideCourseEnabled.objects.filter(course_key=course_id)

        self.assertEqual(res.count(), 0)

    def test_course_enabled_getter_valid(self):
        course_id = course_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            enabled=True,
        )

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)
        self.assertEqual(response.data['response']['enabled'], True)

    def test_course_enabled_getter_404(self):
        course_id = course_keys[1]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 404)

    def test_course_delete(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        AIAsideCourseEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            enabled=True,
        )
        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            unit_key=UsageKey.from_string(unit_id),
            enabled=True,
        )

        courses = AIAsideCourseEnabled.objects.filter(course_key=course_id)
        units = AIAsideUnitEnabled.objects.filter(course_key=course_id)

        self.assertEqual(courses.count(), 1)
        self.assertEqual(units.count(), 1)

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)
        self.assertEqual(courses.count(), 0)
        self.assertEqual(units.count(), 0)

    def test_course_delete_404(self):
        course_id = course_keys[1]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 404)

    def test_unit_enabled_setter_enable_valid(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.post(api_url, {'enabled': True}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)

        res = AIAsideUnitEnabled.objects.filter(course_key=course_id)

        self.assertEqual(res.count(), 1)
        self.assertTrue(res.get().enabled)

    def test_unit_enabled_setter_disable_valid_and_check_duplicates(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            unit_key=UsageKey.from_string(unit_id),
            enabled=True,
        )

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.post(api_url, {'enabled': False}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)

        res = AIAsideUnitEnabled.objects.filter(course_key=course_id)

        self.assertEqual(res.count(), 1)
        self.assertFalse(res.get().enabled)

    def test_unit_enabled_setter_invalid_parameters(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.post(api_url, {'enabled': 'False'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['response']['message'], 'Invalid parameters')

        res = AIAsideUnitEnabled.objects.filter(course_key=course_id)

        self.assertEqual(res.count(), 0)

    def test_unit_enabled_setter_invalid_key(self):
        course_id = course_keys[1]
        unit_id = 'this:is:not_a-valid~key#either!'

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.post(api_url, {'enabled': True}, format='json')
        message = response.data['response']['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(message, 'this:is:not_a-valid~key#either! is not a valid UsageKey')

    def test_unit_enabled_getter_valid(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            unit_key=UsageKey.from_string(unit_id),
            enabled=True,
        )

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)
        self.assertEqual(response.data['response']['enabled'], True)

    def test_unit_enabled_getter_invalid_key(self):
        course_id = course_keys[1]
        unit_id = 'this:is:not_a-valid~key#either!'

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.get(api_url)
        message = response.data['response']['message']
        self.assertEqual(response.status_code, 400)
        self.assertEqual(message, 'this:is:not_a-valid~key#either! is not a valid UsageKey')

    def test_unit_enabled_getter_404(self):
        course_id = course_keys[1]
        unit_id = unit_keys[1]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 404)

    def test_unit_delete(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            unit_key=UsageKey.from_string(unit_id),
            enabled=True,
        )

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['response']['success'], True)

        res = AIAsideUnitEnabled.objects.filter(
            course_key=CourseKey.from_string(course_id),
            unit_key=UsageKey.from_string(unit_id),
            enabled=True,
        )

        self.assertEqual(res.count(), 0)

    def test_unit_delete_404(self):
        course_id = course_keys[1]
        unit_id = unit_keys[1]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 404)

    def test_course_enabled_setter_enable_valid_and_reset(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        units = AIAsideUnitEnabled.objects.filter(course_key=course_id)
        AIAsideUnitEnabled.objects.create(
            course_key=CourseKey.from_string(course_id),
            unit_key=UsageKey.from_string(unit_id),
            enabled=True,
        )

        self.assertEqual(units.count(), 1)

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})

        self.client.post(api_url, {'enabled': True, 'reset': False}, format='json')
        self.assertEqual(units.count(), 1)

        self.client.post(api_url, {'enabled': False, 'reset': True}, format='json')
        self.assertEqual(units.count(), 0)


class TestApiViewsWithoutPermissions(AIAsideAPITestCase):
    """API Endpoint View tests without permissions"""
    def setUp(self):
        super().setUp()
        can_change_summaries_settings.return_value = False
        self.access_mock = patch('ai_aside.platform_imports.can_change_summaries_settings',
                                 can_change_summaries_settings)
        self.access_mock.start()

    def tearDown(self):
        super().tearDown()
        self.access_mock.stop()

    def test_course_configurable_403(self):
        course_id = course_keys[0]

        api_url = reverse('api-course-configurable', kwargs={'course_id': course_id})
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 403)

    def test_get_course_settings_403(self):
        course_id = course_keys[0]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 403)

    def test_post_course_settings_403(self):
        course_id = course_keys[0]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.post(api_url, {'enabled': 'true'}, format='json')

        self.assertEqual(response.status_code, 403)

    def test_delete_course_settings_403(self):
        course_id = course_keys[0]

        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 403)

    def test_get_unit_settings_403(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 403)

    def test_post_unit_settings_403(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.post(api_url, {'enabled': True}, format='json')

        self.assertEqual(response.status_code, 403)

    def test_delete_unit_settings_403(self):
        course_id = course_keys[0]
        unit_id = unit_keys[0]

        api_url = reverse('api-unit-settings', kwargs={
            'course_id': course_id,
            'unit_id': unit_id,
        })
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 403)
