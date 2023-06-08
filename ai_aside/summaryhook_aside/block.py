# pyright: reportMissingImports=false

"""Xblock aside enabling OpenAI driven summaries"""

from datetime import datetime
from html import unescape
from re import sub
from unicodedata import normalize

from django.conf import settings
from django.template import Context, Template
from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import XBlock, XBlockAside

from ai_aside.summaryhook_aside.waffle import summary_enabled, summary_staff_only

summary_fragment = """
<div>&nbsp;</div>
<div class="summary-hook">
  <div summary-launch>
    <div id="launch-summary-button"
      data-url-api="{{data_url_api}}"
      data-course-id="{{data_course_id}}"
      data-content-id="{{data_content_id}}"
      data-handler-url="{{data_handler_url}}"
    >
    </div>
  </div>
  <div id="ai-spot-root"></div>
  <script type="text/javascript" src="{{js_url}}" defer="defer"></script>
</div>
"""


def _format_date(date):
    return date.strftime('%Y-%m-%d %H:%M:%S') if isinstance(date, datetime) else None


def _render_summary(context):
    template = Template(summary_fragment)
    return template.render(Context(context))


def _html_to_text_fallback(html_content):
    """
    Extracts the contents from an HTML string into simple text.
    """
    text = sub('<[^<]+?>', '', html_content)  # Removing HTML tags
    text = unescape(text)  # Unescaping html entities
    text = normalize("NFKD", text)  # Normalizing text
    text = sub(r'\s+', ' ', text)  # Removing extra spaces
    text = text.strip()  # Trim

    return text


def _html_to_text(html_content):
    """
    Extracts the contents from an HTML string into simple text.
    """

    try:
        from xmodule.annotator_mixin import html_to_text  # pylint: disable=import-outside-toplevel
    except ImportError:
        return _html_to_text_fallback(html_content)

    text = html_to_text(html_content)

    return text


def _extract_child_contents(child, category):
    """
    Process the child contents based on its category.
    """

    try:
        # pylint: disable=import-outside-toplevel
        from xmodule.video_block.transcripts_utils import Transcript, get_transcript
    except ImportError:
        return None

    if category == 'html':
        try:
            content_html = child.get_html()
            text = _html_to_text(content_html)

            return text
        except AttributeError:
            return None

    if category == 'video':
        try:
            transcript = get_transcript(child)[0]
            transcript_format = child.transcript_download_format
            text = Transcript.convert(transcript, transcript_format, 'txt')

            return text
        except AttributeError:
            return None

    return None


def _get_children_contents(block):
    """
    Extracts the analyzable contents from its children.
    """
    content_fragments = []

    children = block.get_children()
    for child in children:
        category = getattr(child, 'category', None)
        published_on = getattr(child, 'published_on', None)
        edited_on = getattr(child, 'published_on', None)
        definition_id = str(getattr(getattr(child, 'scope_ids', None), 'def_id', None))
        text = _extract_child_contents(child, category)
        content_fragments.append({
            'definition_id': definition_id,
            'type': category,
            'text': text,
            'published_on': published_on,
            'edited_on': edited_on,
        })

    return content_fragments


def _children_have_summarizable_content(block):
    """
    Only if a unit contains HTML blocks with at least a child
    with sufficient text in them is it worth injecting the summarizer.
    We don't sanitize the content due to performance.
    """

    children = block.get_children()

    for child in children:
        try:
            category = child.category
            if category == 'html' and len(child.get_html()) > settings.SUMMARY_HOOK_MIN_SIZE:
                return True
            if category == 'video':
                return True
        except AttributeError:
            pass

    return False


class SummaryHookAside(XBlockAside):
    """
    XBlock aside that injects AI summary javascript
    """

    def _get_block(self):
        """
        Gets the block wrapped by this aside.
        """

        from xmodule.modulestore.django import modulestore  # pylint: disable=import-error, import-outside-toplevel
        return modulestore().get_item(self.scope_ids.usage_id.usage_key)

    @XBlock.handler
    def summary_handler(self, request=None, suffix=None):  # pylint: disable=unused-argument
        """
        Shell handler to the summary xblock aside.
        """
        block = self._get_block()
        valid = self.should_apply_to_block(block)

        if not valid:
            return Response(status=404)

        published_on = getattr(block, 'published_on', None)
        edited_on = getattr(block, 'published_on', None)
        children_contents = _get_children_contents(block)

        data = []
        for child in children_contents:
            data.append({
                **child,
                'published_on': _format_date(child['published_on']),
                'edited_on': _format_date(child['edited_on']),
            })

        json = {
            'content_id': str(block.scope_ids.usage_id),
            'course_id': str(block.scope_ids.usage_id.course_key),
            'data': data,
            'published_on': _format_date(published_on),
            'edited_on': _format_date(edited_on),
        }
        return Response(json_body=json)

    @XBlockAside.aside_for('student_view')
    def student_view_aside(self, block, context=None):  # pylint: disable=unused-argument
        """
        Renders the aside contents for the student view
        """
        fragment = Fragment('')

        if not _children_have_summarizable_content(block):
            return fragment

        fragment.add_content(
            _render_summary(
                {
                    'data_url_api': settings.SUMMARY_HOOK_HOST,
                    'data_course_id': block.scope_ids.usage_id.course_key,
                    'data_content_id': block.scope_ids.usage_id,
                    'data_handler_url': self.runtime.handler_url(self, 'summary_handler'),
                    'js_url': settings.SUMMARY_HOOK_HOST + settings.SUMMARY_HOOK_JS_PATH,
                }
            )
        )
        return fragment

    @classmethod
    def should_apply_to_block(cls, block):
        """
        Overrides base XBlockAside implementation. Indicates whether this aside should
        apply to a given block type, course, and user.
        """

        if getattr(block, 'category', None) != 'vertical':
            return False
        course_key = block.scope_ids.usage_id.course_key
        if (getattr(block.runtime, 'user_is_staff', False)
                and summary_staff_only(course_key)):
            return True
        return summary_enabled(course_key)
