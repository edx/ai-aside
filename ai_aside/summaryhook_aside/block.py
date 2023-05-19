# pyright: reportMissingImports=false

"""Xblock aside enabling OpenAI driven summaries"""

import time

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


def _render_summary(context):
    template = Template(summary_fragment)
    return template.render(Context(context))


def _children_have_summarizable_content(block):
    """
    Only if a unit contains HTML blocks with sufficient text in them
    is it worth injecting the summarizer.
    """
    children = block.get_children()
    for child in children:
        category = getattr(child, 'category', None)
        if (
                category == 'html'
                and hasattr(child, 'get_html')
                and len(child.get_html()) > settings.SUMMARY_HOOK_MIN_SIZE
        ):
            return True
        # we will eventually require there to be transcripts available to trigger but not yet
        if category == 'video':
            return True
    return False


class SummaryHookAside(XBlockAside):
    """
    XBlock aside that injects AI summary javascript
    """

    def _get_block(self):
        """
        Gets the current aside block.
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

        timestr = time.strftime('%Y-%m-%d %H:%M:%S')
        json = {
            "contentId": "some-content-uuid",
            "courseId": "some-course-uuid",
            "data": [{
                "id": "this-flashy-uuid",
                "type": "VIDEO",
                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec arcu nulla, porttitor sed "
                "volutpat nec, eleifend venenatis leo. Ut luctus libero nisi. Nam elementum scelerisque purus in "
                "pretium. Etiam in interdum nibh, vel dictum ligula. Nunc orci nunc, consequat ut efficitur vitae, "
                "tincidunt non sapien. Integer id sollicitudin erat. Praesent egestas odio quis vulputate ornare. ",
                "created_at": timestr,
                "updated_at": timestr,
            }, {
                "id": "this-stunning-uuid",
                "type": "CONTENT",
                "text": "Nunc dignissim dapibus lectus, a ultrices est tempus quis. Fusce congue lorem et urna tempor "
                "luctus. Phasellus tincidunt mauris at sodales facilisis. Nam tortor erat, porttitor ac laoreet "
                "vitae, molestie non lacus. Praesent eu fermentum lacus. Fusce lectus risus, sagittis ut justo in, "
                "vulputate sodales elit. In vitae tempor nulla. Phasellus tincidunt ante nec enim pharetra.",
                "created_at": timestr,
                "updated_at": timestr,
            }],
            "created_at": timestr,
            "updated_at": timestr,
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
