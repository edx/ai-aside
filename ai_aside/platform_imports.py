# pyright: reportMissingImports=false

"""
Contain all imported functions coming out of the platform.

We know these functions will be available at run time, but they
cannot be imported normally.
"""


def get_text_transcript(video_block):
    """Get the transcript for a video block in text format, or None."""
    # pylint: disable=import-error, import-outside-toplevel
    from xmodule.exceptions import NotFoundError
    from xmodule.video_block.transcripts_utils import get_transcript
    try:
        transcript, _, _ = get_transcript(video_block, output_format='txt')
    except NotFoundError:
        # some old videos have no transcripts, just accept that reality
        return None
    return transcript


def get_block(usage_key):
    """Get a block from the module store given the usage key."""
    # pylint: disable=import-error, import-outside-toplevel
    from xmodule.modulestore.django import modulestore
    return modulestore().get_item(usage_key)


def can_change_summaries_settings(user, course_key):
    """Check if the user can change the summaries settings by checking for studio write access."""
    # pylint: disable=import-error, import-outside-toplevel
    from common.djangoapps.student.auth import has_studio_write_access
    return has_studio_write_access(user, course_key)
