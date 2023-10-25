"""
Xblock aside enabling text extraction for various AI uses.

Currently duplicates a lot of code from the regular aside with the theory we might move it,
or want to mess with it during innovation week. If it lives here forever we can collapse
it all back together.
"""

import logging
from html.parser import HTMLParser
from re import sub

from django.conf import settings
from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import XBlock, XBlockAside

log = logging.getLogger(__name__)

def extract_block_content(block):
    """Extract content for a block and all children recursively."""
    content = []
    local_content = extract_text_content(block)
    if local_content is not None:
        content.append(local_content)

    children = block.get_children()
    for child in children:
        child_content = extract_block_content(child)
        content.extend(child_content)

    return content


def extract_text_content(block):
    """Extract text content for a block of known type, otherwise none."""
    category = getattr(block, 'category', None)

    if category == 'html':
        content_html = block.get_html()
        text = html_to_text(content_html)
        return text

    if category == 'video':
        transcript = get_text_transcript(block)  # may be None
        return transcript

    return None


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


def cleanup_text(text):
    """
    Remove litter from replacing or manipulating text.
    """
    stripped = sub(r'[^\S\r\n]+', ' ', text)  # Removing extra spaces
    stripped = sub(r'\n{2,}', '\n', stripped)  # Removing extra new lines
    stripped = sub(r'(\s+)?\n(\s+)?', '\n', stripped)  # Removing starting extra spacesbetween new lines
    stripped = sub(r'(^(\s+)\n?)|(\n(\s+)?$)', '', stripped)  # Trim

    return stripped


class _HTMLToTextHelper(HTMLParser):  # lint-amnesty, pylint: disable=abstract-method
    """
    Helper function for html_to_text below.
    """

    _is_content = True

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_starttag(self, tag, _):
        """On each tag, check whether this is a tag we think is content."""
        tags_to_filter = getattr(settings, 'HTML_TAGS_TO_REMOVE', None)
        self._is_content = not (tags_to_filter and tag in tags_to_filter)

    def handle_data(self, data):
        """Handle tag data by appending text we think is content."""
        if self._is_content:
            self.fed.append(data)

    def handle_entityref(self, name):
        """If there is an entity, append the reference to the text."""
        if self._is_content:
            self.fed.append('&%s;' % name)

    def get_data(self):
        """Join together the separate data chunks into one cohesive string."""
        return ''.join(self.fed)


def html_to_text(html):
    """Strip the html tags off of the text to return plaintext."""
    htmlstripper = _HTMLToTextHelper()
    htmlstripper.feed(html)
    text = htmlstripper.get_data()
    text = cleanup_text(text)

    return text


def _staff_user(block):
    return getattr(block.runtime, 'user_is_staff', False)


class ExtractorAside(XBlockAside):
    """
    XBlock aside that injects AI summary javascript.
    """

    # has no views, just provides this extraction handler


    @XBlock.handler
    def extract_handler(self, request=None, suffix=None):  # pylint: disable=unused-argument
        """
        Extract and return card useful text for AI from any block.

        Only services and staff users are allowed to fetch summary text, everyone else
        gets an unhelpful 403.

        handler URLs can be made from block IDs by escaping the : to $: and dropping them into the handler
        URL format

        so for block-v1:edX+DemoX+Demo_Course+type@chapter+block@d8a6192ade314473a78242dfeedfbf5b on devstack

        http://localhost:18010/xblock/aside-usage-v2:block-v1$:edX+DemoX+Demo_Course+type@chapter+block@d8a6192ade314473a78242dfeedfbf5b::extractor_aside/handler/extract_handler
        """
        if not _staff_user(self):
            return Response(status=403)

        block = get_block(self.scope_ids.usage_id.usage_key)
        valid = self.should_apply_to_block(block)  # currently just "true" from parent

        if not valid:
            return Response(status=404)

        content = extract_block_content(block)

        body = {
            'content': content,
        }
        return Response(json_body=body)
