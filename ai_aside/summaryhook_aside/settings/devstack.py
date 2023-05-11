"""Devstack settings values."""

import os
from os.path import abspath, dirname, join


def plugin_settings(settings):
    """ Override/set summary hook devstack settings"""
    settings.SUMMARY_HOOK_HOST = 'http://localhost:3000'
    settings.SUMMARY_HOOK_JS_PATH = '/static/js/main.js'
    settings.SUMMARY_HOOK_MIN_SIZE = 500
    if os.path.isfile(join(dirname(abspath(__file__)), 'private.py')):
        from .private import plugin_settings_override  # pylint: disable=import-outside-toplevel,import-error
        plugin_settings_override(settings)
