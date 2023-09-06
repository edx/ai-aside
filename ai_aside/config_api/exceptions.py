"""
Custom exceptions for ai-aside
"""
from rest_framework import status


class AiAsideException(Exception):
    """
    A common base class for all exceptions
    """
    http_status = status.HTTP_400_BAD_REQUEST


class AiAsideNotFoundException(AiAsideException):
    """
    A 404 exception class
    """
    http_status = status.HTTP_404_NOT_FOUND
