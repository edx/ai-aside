# pyright: reportMissingImports=false

"""
Contain all imported functions coming out of the platform.

We know these functions will be available at run time, but they
cannot be imported normally.
"""


def get_text_transcript(video_block):
    """Get the transcript for a video block in text format."""
    # pylint: disable=import-error, import-outside-toplevel
    from xmodule.video_block.transcripts_utils import get_transcript
    transcript, _, _ = get_transcript(video_block, output_format='txt')
    return transcript


def get_block(usage_key):
    """Get a block from the module store given the usage key."""
    # pylint: disable=import-error, import-outside-toplevel
    from xmodule.modulestore.django import modulestore
    return modulestore().get_item(usage_key)
