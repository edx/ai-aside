"""
Config API Utilities
"""
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ai_aside.config_api.exceptions import AiAsideException
from ai_aside.config_api.permissions import HasStudioWriteAccess


class APIResponse(Response):
    """API Response"""
    def __init__(self, data=None, http_status=None, content_type=None, success=False):
        _status = http_status or status.HTTP_200_OK
        data = data or {}
        reply = {'response': {'success': success}}
        reply['response'].update(data)
        super().__init__(data=reply, status=_status, content_type=content_type)


class AiAsideAPIView(APIView):
    """
    Base API View with authentication and permissions.
    """

    authentication_classes = (JwtAuthentication, SessionAuthentication,)
    permission_classes = (HasStudioWriteAccess,)


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
