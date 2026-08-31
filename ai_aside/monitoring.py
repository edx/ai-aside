"""
Datadog monitoring helpers for Xpert Summary (ai-aside) events (LP-919).

Wraps edx_django_utils.monitoring so failures normally caught and swallowed
(to protect the LMS) still show up as errors/metrics in DataDog, instead of
only in application logs.
"""

import functools
import logging

from edx_django_utils.monitoring import (
    accumulate,
    increment,
    record_exception,
    set_custom_attribute,
    set_custom_attributes_for_course_key,
)

log = logging.getLogger(__name__)


def _never_raises(func):
    """Wrap func so a monitoring failure never breaks the code path it observes."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:  # pylint: disable=broad-exception-caught
            log.exception('ai-aside monitoring failed in %s', func.__name__)
            return None
    return wrapper


def _tag_usage(usage_id):
    """Attach course/unit identifying attributes to the current request."""
    set_custom_attributes_for_course_key(usage_id.course_key)
    set_custom_attribute('xpert_summary.usage_id', str(usage_id))


@_never_raises
def monitor_render_failure(usage_id, exception):
    """Record that rendering the summary hook raised and was suppressed."""
    _tag_usage(usage_id)
    set_custom_attribute('xpert_summary.render_result', 'error')
    set_custom_attribute('xpert_summary.error_class', exception.__class__.__name__)
    increment('xpert_summary.render.error')
    record_exception()


@_never_raises
def monitor_should_apply_failure(usage_id, exception):
    """Record that the should_apply_to_block check raised and was suppressed."""
    _tag_usage(usage_id)
    set_custom_attribute('xpert_summary.should_apply_result', 'error')
    set_custom_attribute('xpert_summary.error_class', exception.__class__.__name__)
    increment('xpert_summary.should_apply.error')
    record_exception()


@_never_raises
def monitor_handler_result(usage_id, result):
    """Record the outcome of a summary_handler request: forbidden/not_found/empty/success/error."""
    _tag_usage(usage_id)
    set_custom_attribute('xpert_summary.handler_result', result)
    increment(f'xpert_summary.handler.{result}')


def monitor_handler_invocation(usage_id):
    """Record summary_handler invocation, unconditionally (before the permission check)."""
    _tag_usage(usage_id)
    increment('ai_aside.handler.requests')


def monitor_extraction_metrics(usage_id, duration_ms, content_size, block_count):
    """Record content-extraction latency/size/block-count for a summary_handler call."""
    _tag_usage(usage_id)
    set_custom_attribute('ai_aside.handler.extraction_time_ms', duration_ms)
    set_custom_attribute('ai_aside.handler.content_size', content_size)
    set_custom_attribute('ai_aside.handler.block_count', block_count)
    accumulate('ai_aside.handler.extraction_time', duration_ms)
    accumulate('ai_aside.handler.content_size', content_size)


@_never_raises
def monitor_extraction_error(usage_id, exception, source):
    """Record that content extraction raised; source is 'handler' or 'aside'."""
    _tag_usage(usage_id)
    set_custom_attribute('ai_aside.extraction.error_class', exception.__class__.__name__)
    set_custom_attribute('ai_aside.extraction.source', source)
    increment('ai_aside.aside.extraction_errors')
    record_exception()


def monitor_aside_injection(usage_id, user_role, duration_ms):
    """Record that the summary aside was injected into a unit's student view."""
    _tag_usage(usage_id)
    set_custom_attribute('ai_aside.aside.user_role', user_role)
    set_custom_attribute('ai_aside.aside.render_time_ms', duration_ms)
    accumulate('ai_aside.aside.render_time', duration_ms)
    increment('ai_aside.aside.injections')


def monitor_config_api_request(method, course_id, unit_id, action, status, duration_ms, exception=None):
    """Record a config API request's call count, per-status breakdown, and latency."""
    set_custom_attribute('ai_aside.config_api.method', method)
    set_custom_attribute('ai_aside.config_api.course_id', course_id)
    if unit_id is not None:
        set_custom_attribute('ai_aside.config_api.unit_id', unit_id)
    set_custom_attribute('ai_aside.config_api.action', action)
    set_custom_attribute('ai_aside.config_api.status', status)
    set_custom_attribute('ai_aside.config_api.duration_ms', duration_ms)
    increment('ai_aside.config_api.requests')
    increment(f'ai_aside.config_api.requests.{status}')

    if exception is not None:
        set_custom_attribute('ai_aside.config_api.error_class', exception.__class__.__name__)
        # record_exception() is called in AiAsideAPIView.handle_exception(), where the
        # exception context is still active; calling it again here double-counts the error.
