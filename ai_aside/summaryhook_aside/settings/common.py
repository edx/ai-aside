"""Default settings load from environment"""


def plugin_settings(settings):
    """
    Get summary hook aside settings from calling application
    """
    env_tokens = getattr(settings, 'ENV_TOKENS', {})
    settings.SUMMARY_HOOK_HOST = env_tokens.get('SUMMARY_HOOK_HOST', '')
    settings.SUMMARY_HOOK_JS_PATH = env_tokens.get('SUMMARY_HOOK_JS_PATH', '')
