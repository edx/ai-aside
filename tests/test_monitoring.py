"""Tests for ai_aside monitoring helpers."""
import unittest
from unittest.mock import patch

from opaque_keys.edx.keys import UsageKey

from ai_aside import monitoring

usage_id = UsageKey.from_string('block-v1:edX+A+B+type@vertical+block@verticalD')


class TestMonitoring(unittest.TestCase):
    """Tests for the xpert_summary monitoring helper functions."""

    @patch('ai_aside.monitoring.record_exception')
    @patch('ai_aside.monitoring.increment')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_render_failure(self, mock_course_attrs, mock_attr, mock_increment, mock_record):
        exception = ValueError('boom')

        monitoring.monitor_render_failure(usage_id, exception)

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('xpert_summary.render_result', 'error')
        mock_attr.assert_any_call('xpert_summary.error_class', 'ValueError')
        mock_increment.assert_called_once_with('xpert_summary.render.error')
        mock_record.assert_called_once_with()

    @patch('ai_aside.monitoring.record_exception')
    @patch('ai_aside.monitoring.increment')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_should_apply_failure(self, mock_course_attrs, mock_attr, mock_increment, mock_record):
        exception = KeyError('missing')

        monitoring.monitor_should_apply_failure(usage_id, exception)

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('xpert_summary.should_apply_result', 'error')
        mock_attr.assert_any_call('xpert_summary.error_class', 'KeyError')
        mock_increment.assert_called_once_with('xpert_summary.should_apply.error')
        mock_record.assert_called_once_with()

    @patch('ai_aside.monitoring.increment')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_handler_result(self, mock_course_attrs, mock_attr, mock_increment):
        monitoring.monitor_handler_result(usage_id, 'success')

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('xpert_summary.handler_result', 'success')
        mock_increment.assert_called_once_with('xpert_summary.handler.success')

    @patch('ai_aside.monitoring.increment')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_handler_invocation(self, mock_course_attrs, mock_attr, mock_increment):
        monitoring.monitor_handler_invocation(usage_id)

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('xpert_summary.usage_id', str(usage_id))
        mock_increment.assert_called_once_with('ai_aside.handler.requests')

    @patch('ai_aside.monitoring.accumulate')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_extraction_metrics(self, mock_course_attrs, mock_attr, mock_accumulate):
        monitoring.monitor_extraction_metrics(usage_id, 12.5, 4096, 3)

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('ai_aside.handler.extraction_time_ms', 12.5)
        mock_attr.assert_any_call('ai_aside.handler.content_size', 4096)
        mock_attr.assert_any_call('ai_aside.handler.block_count', 3)
        mock_accumulate.assert_any_call('ai_aside.handler.extraction_time', 12.5)
        mock_accumulate.assert_any_call('ai_aside.handler.content_size', 4096)

    @patch('ai_aside.monitoring.record_exception')
    @patch('ai_aside.monitoring.increment')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_extraction_error(self, mock_course_attrs, mock_attr, mock_increment, mock_record):
        exception = RuntimeError('kaboom')

        monitoring.monitor_extraction_error(usage_id, exception, source='handler')

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('ai_aside.extraction.error_class', 'RuntimeError')
        mock_attr.assert_any_call('ai_aside.extraction.source', 'handler')
        mock_increment.assert_called_once_with('ai_aside.aside.extraction_errors')
        mock_record.assert_called_once_with()

    @patch('ai_aside.monitoring.accumulate')
    @patch('ai_aside.monitoring.increment')
    @patch('ai_aside.monitoring.set_custom_attribute')
    @patch('ai_aside.monitoring.set_custom_attributes_for_course_key')
    def test_monitor_aside_injection(self, mock_course_attrs, mock_attr, mock_increment, mock_accumulate):
        monitoring.monitor_aside_injection(usage_id, 'student audit', 7.25)

        mock_course_attrs.assert_called_once_with(usage_id.course_key)
        mock_attr.assert_any_call('ai_aside.aside.user_role', 'student audit')
        mock_attr.assert_any_call('ai_aside.aside.render_time_ms', 7.25)
        mock_accumulate.assert_called_once_with('ai_aside.aside.render_time', 7.25)
        mock_increment.assert_called_once_with('ai_aside.aside.injections')


if __name__ == '__main__':
    unittest.main()
