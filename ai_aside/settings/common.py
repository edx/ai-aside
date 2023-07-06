"""
ai_aside common settings.
"""


def plugin_settings(settings):
    """
    Get aside settings from calling application
    """
    env_tokens = getattr(settings, 'ENV_TOKENS', {})
    settings.SUMMARY_HOOK_HOST = env_tokens.get('SUMMARY_HOOK_HOST', '')
    settings.SUMMARY_HOOK_JS_PATH = env_tokens.get('SUMMARY_HOOK_JS_PATH', '')
    settings.AISPOT_LMS_NAME = env_tokens.get('AISPOT_LMS_NAME', '')
    settings.HTML_TAGS_TO_REMOVE = ['script', 'style']
