"""
Config API Utilities
"""
import logging
import time

from edx_django_utils.monitoring import record_exception
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.exceptions import ParseError, UnsupportedMediaType
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_aside.config_api.exceptions import AiAsideException
from ai_aside.config_api.permissions import HasStudioWriteAccess
from ai_aside.monitoring import monitor_config_api_request

log = logging.getLogger(__name__)


class APIResponse(Response):
    """API Response"""
    def __init__(self, data=None, http_status=None, content_type=None, success=False):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {'response': {'success': success}}
        reply['response'].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)


def _config_api_action(request):
    """Derive the 'action' tag for a config API request from its method/payload."""
    if request.method == 'POST':
        try:
            request_data = request.data
        except (ParseError, UnsupportedMediaType, ValueError, TypeError):
            return 'update'

        reset = request_data.get('reset') if hasattr(request_data, 'get') else None
        if reset:
            return 'reset'
        enabled = request_data.get('enabled') if hasattr(request_data, 'get') else None
        if enabled is True:
            return 'enable'
        if enabled is False:
            return 'disable'
        return 'update'
    if request.method == 'DELETE':
        return 'reset'
    return 'read'


def _config_api_status(status_code):
    """Bucket an HTTP status code into a small set of alertable status tags."""
    if 200 <= status_code < 300:
        return 'success'
    if status_code == 401:
        return 'unauthenticated'
    if status_code == 403:
        return 'forbidden'
    if status_code == 404:
        return 'not_found'
    if 400 <= status_code < 500:
        return 'client_error'
    return 'error'


class AiAsideAPIView(APIView):
    """Base API View with authentication/permissions, centrally instrumented with Datadog metrics."""

    authentication_classes = (JwtAuthentication, SessionAuthentication,)
    permission_classes = (HasStudioWriteAccess,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._monitoring_start = None
        self._monitoring_exception = None

    def initial(self, request, *args, **kwargs):
        self._monitoring_start = time.monotonic()
        self._monitoring_exception = None
        super().initial(request, *args, **kwargs)

    def handle_exception(self, exc):
        self._monitoring_exception = exc
        record_exception()
        return super().handle_exception(exc)

    def dispatch(self, request, *args, **kwargs):
        # try/finally (rather than finalize_response) so monitoring fires for
        # uncaught exceptions too, which DRF re-raises without ever calling
        # finalize_response.
        try:
            return super().dispatch(request, *args, **kwargs)
        finally:
            self._emit_monitoring(getattr(self, 'request', request), getattr(self, 'response', None), kwargs)

    def _emit_monitoring(self, request, response, kwargs):
        """Report the outcome of this request to Datadog, if initial() ran."""
        if self._monitoring_start is None:
            return

        try:
            duration_ms = (time.monotonic() - self._monitoring_start) * 1000
            status_code = response.status_code if response is not None else 500
            monitor_config_api_request(
                method=request.method,
                course_id=kwargs.get('course_id'),
                unit_id=kwargs.get('unit_id'),
                action=_config_api_action(request),
                status=_config_api_status(status_code),
                duration_ms=duration_ms,
                exception=self._monitoring_exception,
            )
        except Exception:  # pylint: disable=broad-exception-caught
            log.exception('ai-aside config API monitoring failed')


def handle_errors(view_func):
    """
    Wrapper which handles our standard exception.

    We cannot do this by overriding handle_exception as you might expect,
    because the newrelic wrapper sits between the view function and the
    handle_exception and logs it, which makes our expected exceptions seem
    harmful. So we'll handle those before newrelic can see them.
    """
    def wrapped_viewfunc(self_, request, **kwargs):
        try:
            return view_func(self_, request, **kwargs)
        except AiAsideException as exc:
            return APIResponse(http_status=exc.http_status, data={'message': str(exc)})
    return wrapped_viewfunc
