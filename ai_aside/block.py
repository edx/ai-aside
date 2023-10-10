"""Xblock aside enabling OpenAI driven summaries."""

import logging
from datetime import datetime

from django.conf import settings
from django.template import Context, Template
from web_fragments.fragment import Fragment
from webob import Response
from xblock.core import XBlock, XBlockAside

from ai_aside.config_api.api import is_summary_enabled
from ai_aside.constants import ATTR_KEY_USER_ID, ATTR_KEY_USER_ROLE
from ai_aside.platform_imports import get_block, get_text_transcript
from ai_aside.text_utils import html_to_text
from ai_aside.waffle import summaries_configuration_enabled as ff_is_summary_config_enabled
from ai_aside.waffle import summary_staff_only as ff_summary_staff_only

log = logging.getLogger(__name__)

# map block types to what ai-spot expects for content types
CATEGORY_TYPE_MAP = {
    "html": "TEXT",
    "video": "VIDEO",
}

summary_fragment = """
<div>&nbsp;</div>
<div class="summary-hook">
  <div summary-launch>
    <div id="launch-summary-button"
      data-url-api="{{data_url_api}}"
      data-course-id="{{data_course_id}}"
      data-content-id="{{data_content_id}}"
      data-handler-url="{{data_handler_url}}"
      data-last-updated="{{data_last_updated}}"
      data-user-role="{{data_user_role}}"
    >
    </div>
  </div>
  <div id="ai-spot-root"></div>
  <script type="text/javascript" src="{{js_url}}" defer="defer"></script>
</div>
"""


def _format_date(date):
    return date.isoformat() if isinstance(date, datetime) else None


def _staff_user(block):
    return getattr(block.runtime, 'user_is_staff', False)


def _render_summary(context):
    template = Template(summary_fragment)
    return template.render(Context(context))


def _extract_child_contents(child, category):
    """
    Process the child contents based on its category.

    Returns a string or None if there are no contents available.
    """
    if category == 'html':
        content_html = child.get_html()
        text = html_to_text(content_html)

        return text

    if category == 'video':
        transcript = get_text_transcript(child)  # may be None
        return transcript

    return None


def _parse_children_contents(block):
    """
    Extract the analyzable contents from block children.

    Returns length and an item list.
    """
    if not _check_summarizable(block):
        return 0, []

    content_items = []

    children = block.get_children()
    content_length = 0
    for child in children:
        category = getattr(child, 'category', None)
        category_type = CATEGORY_TYPE_MAP.get(category)
        published_on = getattr(child, 'published_on', None)
        edited_on = getattr(child, 'edited_on', None)
        definition_id = str(getattr(getattr(child, 'scope_ids', None), 'def_id', None))
        text = _extract_child_contents(child, category)

        if text is None:
            continue

        content_length += len(text)
        content_items.append({
            'definition_id': definition_id,
            'content_type': category_type,
            'content_text': text,
            'published_on': published_on,
            'edited_on': edited_on,
        })

    return content_length, content_items


def _check_summarizable(block):
    """
    First pass check if a block has or does not have sufficient text to summarize.

    We don't sanitize the content due to performance in this first check.
    """
    children = block.get_children()

    content_length = 0

    for child in children:
        category = child.category
        if category == 'html':
            content_length += len(child.get_html())
            if content_length > settings.SUMMARY_HOOK_MIN_SIZE:
                return True

        if category == 'video':
            return True

    return False


def _render_hook_fragment(user_role_string, handler_url, block, summary_items):
    """
    Create hook Fragment from block and summarized children.

    Gathers data for the summary hook HTML, passes it into _render_summary
    to get the HTML and packages that into a Fragment.
    """
    last_published = getattr(block, 'published_on', None)
    last_edited = getattr(block, 'edited_on', None)
    usage_id = block.scope_ids.usage_id
    course_key = usage_id.course_key

    for item in summary_items:
        published = item['published_on']
        edited = item['edited_on']
        if published and published > last_published:
            last_published = published
        if edited and edited > last_edited:
            last_edited = edited

    # we only need to know when the last time was that anything happened
    last_updated = last_published
    if last_edited > last_published:
        last_updated = last_edited

    fragment = Fragment('')
    fragment.add_content(
        _render_summary(
            {
                'data_url_api': settings.SUMMARY_HOOK_HOST,
                'data_course_id': course_key,
                'data_content_id': usage_id,
                'data_handler_url': handler_url,
                'data_last_updated': _format_date(last_updated),
                'data_user_role': user_role_string,
                'js_url': settings.SUMMARY_HOOK_HOST + settings.SUMMARY_HOOK_JS_PATH,
            }
        )
    )
    return fragment


@XBlock.needs('user')
@XBlock.needs('credit')
class SummaryHookAside(XBlockAside):
    """
    XBlock aside that injects AI summary javascript.
    """

    @XBlock.handler
    def summary_handler(self, request=None, suffix=None):  # pylint: disable=unused-argument
        """
        Extract and return summarizable text from unit children.

        Only services and staff users are allowed to fetch summary text, everyone else
        gets an unhelpful 403.
        """
        if not _staff_user(self):
            return Response(status=403)

        block = get_block(self.scope_ids.usage_id.usage_key)
        valid = self.should_apply_to_block(block)

        if not valid:
            return Response(status=404)

        published_on = getattr(block, 'published_on', None)
        edited_on = getattr(block, 'edited_on', None)

        data = []

        length, items = _parse_children_contents(block)

        if length < settings.SUMMARY_HOOK_MIN_SIZE or len(items) < 1:
            return Response(json_body={'data': []})

        for item in items:
            data.append({
                **item,
                'published_on': _format_date(item['published_on']),
                'edited_on': _format_date(item['edited_on']),
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
        Render the aside contents for the student view.

        Returns a Fragment.

        This function absorbs all exceptions to protect the LMS,
        delegating real work to _student_view_can_throw
        """
        try:
            return self._student_view_can_throw(block)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            usage_id = block.scope_ids.usage_id
            log.error(f'Summary hook aside suppressed exception on {usage_id} during student_view_aside: {ex}')
            return Fragment('')

    def _student_view_can_throw(self, block):
        """
        Render the aside contents for the student view.

        Returns a Fragment.

        This function can throw exceptions.
        """
        length, items = _parse_children_contents(block)

        if length < settings.SUMMARY_HOOK_MIN_SIZE:
            return Fragment('')

        usage_id = block.scope_ids.usage_id
        log.info(f'Summary hook injecting into {usage_id}')

        return _render_hook_fragment(
            self._user_role_string(usage_id.course_key),
            self._summary_handler_url(),
            block,
            items)

    def _summary_handler_url(self):
        """
        Generate the summary handler URL for this block.

        A separate function to handle overrides required
        for the unusual use of the handler (non-edx codebase edx service)
        and to override the URL for use in devstack.
        """
        # thirdparty=true gives the full host name and unauthenticated handler
        handler_url = self.runtime.handler_url(self, 'summary_handler', thirdparty=True)
        # but we want the authenticated handler
        handler_url = handler_url.replace('handler_noauth', 'handler')
        # enable ai-spot to see the LMS when they are installed together in devstack
        aispot_lms_name = settings.AISPOT_LMS_NAME
        if aispot_lms_name != '':
            handler_url = handler_url.replace('localhost', aispot_lms_name)
        return handler_url

    def _user_role_string(self, course_key):
        return self._user_role_string_from_services(
            self.runtime.service(self, 'user'),
            self.runtime.service(self, 'credit'),
            course_key)

    @classmethod
    def _user_role_string_from_services(cls, user_service, credit_service, course_key):
        """
        Determine and construct the user_role string that gets injected into the block.
        """
        user_role = 'unknown'
        user = user_service.get_current_user()
        if user is not None:
            user_role = user.opt_attrs.get(ATTR_KEY_USER_ROLE)
            user_enrollment = credit_service.get_credit_state(
                user.opt_attrs.get(ATTR_KEY_USER_ID), course_key)

            if user_enrollment is not None and user_enrollment.get('enrollment_mode') is not None:
                user_role = user_role + " " + user_enrollment.get('enrollment_mode')

        return user_role

    @classmethod
    def should_apply_to_block(cls, block):
        """
        Determine whether this aside should apply to a given block type, course, and user.

        This function absorbs all exceptions to protect the LMS,
        delegating real work to _should_apply_throws.
        """
        try:
            return cls._should_apply_can_throw(block)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            usage_id = block.scope_ids.usage_id
            log.error(f'Summary hook aside suppressed exception on {usage_id} during should_apply_to_block: {ex}')
            return False

    @classmethod
    def _should_apply_can_throw(cls, block):
        """
        Determine whether this aside should apply to a given block type, course, and user.

        This function can throw exceptions.
        """
        if getattr(block, 'category', None) != 'vertical':
            return False

        course_key = block.scope_ids.usage_id.course_key
        unit_key = block.scope_ids.usage_id

        if _staff_user(block) and ff_summary_staff_only(course_key):
            return True

        if ff_is_summary_config_enabled(course_key):
            return is_summary_enabled(course_key, unit_key)

        return False
