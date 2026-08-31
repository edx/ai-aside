"""Tests for the Datadog monitoring instrumentation on the config API views."""
from unittest.mock import Mock, patch

import pytest
from django.urls import reverse
from rest_framework.exceptions import ParseError
from rest_framework.test import APIRequestFactory, force_authenticate

from test_utils import AIAsideAPITestCase, user_mock

course_id = 'course-v1:edX+DemoX+Demo_Course'
unit_id = 'block-v1:edX+DemoX+Demo_Course+type@vertical+block@vertical_0270f6de40fc'

can_change_summaries_settings = Mock()


class TestConfigApiMonitoring(AIAsideAPITestCase):
    """Verify that config API requests emit ai_aside.config_api.requests metrics."""

    def setUp(self):
        super().setUp()
        can_change_summaries_settings.return_value = True
        self.can_change_summaries_settings = can_change_summaries_settings
        self.access_mock = patch(
            'ai_aside.config_api.permissions.can_change_summaries_settings',
            can_change_summaries_settings,
        )
        self.access_mock.start()

    def tearDown(self):
        super().tearDown()
        self.access_mock.stop()

    @patch('ai_aside.config_api.view_utils.monitor_config_api_request')
    def test_get_course_settings_reports_success(self, mock_monitor):
        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 404)  # no settings created yet
        mock_monitor.assert_called_once()
        _, kwargs = mock_monitor.call_args
        self.assertEqual(kwargs['method'], 'GET')
        self.assertEqual(kwargs['course_id'], course_id)
        self.assertIsNone(kwargs['unit_id'])
        self.assertEqual(kwargs['action'], 'read')
        self.assertEqual(kwargs['status'], 'not_found')
        self.assertIsInstance(kwargs['duration_ms'], float)
        self.assertIsNone(kwargs['exception'])

    @patch('ai_aside.config_api.view_utils.monitor_config_api_request')
    def test_post_course_settings_enable_tags_action(self, mock_monitor):
        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.post(api_url, {'enabled': True}, format='json')

        self.assertEqual(response.status_code, 200)
        _, kwargs = mock_monitor.call_args
        self.assertEqual(kwargs['method'], 'POST')
        self.assertEqual(kwargs['action'], 'enable')
        self.assertEqual(kwargs['status'], 'success')

    @patch('ai_aside.config_api.view_utils.monitor_config_api_request')
    def test_post_course_settings_disable_tags_action(self, mock_monitor):
        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})
        response = self.client.post(api_url, {'enabled': False}, format='json')

        self.assertEqual(response.status_code, 200)
        _, kwargs = mock_monitor.call_args
        self.assertEqual(kwargs['action'], 'disable')

    @patch('ai_aside.config_api.view_utils.monitor_config_api_request')
    def test_delete_unit_settings_tags_course_and_unit(self, mock_monitor):
        api_url = reverse('api-unit-settings', kwargs={'course_id': course_id, 'unit_id': unit_id})
        response = self.client.delete(api_url)

        self.assertEqual(response.status_code, 404)  # nothing to delete yet
        _, kwargs = mock_monitor.call_args
        self.assertEqual(kwargs['method'], 'DELETE')
        self.assertEqual(kwargs['course_id'], course_id)
        self.assertEqual(kwargs['unit_id'], unit_id)
        self.assertEqual(kwargs['action'], 'reset')
        self.assertEqual(kwargs['status'], 'not_found')

    @patch('ai_aside.config_api.view_utils.monitor_config_api_request')
    def test_forbidden_request_reports_forbidden_status_and_exception(self, mock_monitor):
        self.can_change_summaries_settings.return_value = False
        api_url = reverse('api-course-settings', kwargs={'course_id': course_id})

        response = self.client.get(api_url)

        self.assertEqual(response.status_code, 403)
        mock_monitor.assert_called_once()
        _, kwargs = mock_monitor.call_args
        self.assertEqual(kwargs['status'], 'forbidden')
        self.assertIsNotNone(kwargs['exception'])

    @patch('ai_aside.config_api.view_utils.monitor_config_api_request')
    @patch('ai_aside.config_api.views.get_course_settings')
    def test_uncaught_exception_is_still_reported(self, mock_get_settings, mock_monitor):
        """An uncaught (non-API) exception must still be monitored, via dispatch()'s try/finally."""
        # Imported lazily so setUp()'s auth patches are active before this binds JwtAuthentication.
        from ai_aside.config_api.views import CourseEnabledAPIView  # pylint: disable=import-outside-toplevel

        mock_get_settings.side_effect = RuntimeError('boom')
        request = APIRequestFactory().get(f'/ai_aside/v1/{course_id}')
        force_authenticate(request, user=user_mock)
        view = CourseEnabledAPIView.as_view()

        with pytest.raises(RuntimeError):
            view(request, course_id=course_id)

        mock_monitor.assert_called_once()
        _, kwargs = mock_monitor.call_args
        self.assertEqual(kwargs['status'], 'error')
        self.assertIsInstance(kwargs['exception'], RuntimeError)

    def test_config_api_action_post_malformed_data_falls_back_to_update(self):
        # pylint: disable=import-outside-toplevel
        from ai_aside.config_api.view_utils import _config_api_action

        class MalformedPostRequest:
            """Request stub whose data property raises ParseError."""
            method = 'POST'

            @property
            def data(self):
                raise ParseError('malformed body')

        self.assertEqual(_config_api_action(MalformedPostRequest()), 'update')
