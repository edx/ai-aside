"""devstack settings values."""

import os
from os.path import abspath, dirname, join


def plugin_settings(settings):
    """ Override/set summary hook devstack settings"""
    settings.SUMMARY_HOOK_HOST = 'http://ai-spot.2u.localhost'
    settings.SUMMARY_HOOK_JS_PATH = '/static/js/main.js'
    settings.SUMMARY_HOOK_MIN_SIZE = 500
    settings.AISPOT_LMS_NAME = 'lms'  # in docker ai-spot sees the LMS as 'lms' not 'localhost'
    if os.path.isfile(join(dirname(abspath(__file__)), 'private.py')):
        from .private import plugin_settings_override  # pylint: disable=import-outside-toplevel,import-error
        plugin_settings_override(settings)
