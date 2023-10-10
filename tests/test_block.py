"""Tests for the block."""
import unittest
from datetime import datetime
from textwrap import dedent
from unittest.mock import MagicMock, Mock, call, patch

from django.test import TestCase, override_settings
from opaque_keys.edx.keys import UsageKey

from ai_aside.block import (
    SummaryHookAside,
    _check_summarizable,
    _extract_child_contents,
    _format_date,
    _parse_children_contents,
    _render_hook_fragment,
)

fake_transcript = 'This is the text version from the transcript'
date1 = datetime(2023, 1, 2, 3, 4, 5)
date2 = datetime(2023, 6, 7, 8, 9, 10)


def fake_get_transcript(child, lang=None, output_format='SRT', youtube_id=None):  # pylint: disable=unused-argument
    return (fake_transcript, 'unused', 'unused')


class FakeChild:
    """Fake child block for testing"""
    transcript_download_format = 'txt'

    def __init__(self, category, test_id='test-id', test_html='<div>This is a test</div>'):
        self.category = category
        self.published_on = 'published-on-{}'.format(test_id)
        self.edited_on = 'edited-on-{}'.format(test_id)
        self.scope_ids = lambda: None
        self.scope_ids.def_id = 'def-id-{}'.format(test_id)
        self.html = test_html
        self.transcript = fake_transcript

    def get_html(self):
        if self.category == 'html':
            return self.html

        return None


class FakeBlock:
    "Fake block for testing, returns given children"
    def __init__(self, children):
        self.children = children
        self.scope_ids = lambda: None
        self.scope_ids.usage_id = UsageKey.from_string('block-v1:edX+A+B+type@vertical+block@verticalD')
        self.edited_on = date1
        self.published_on = date1
        my_runtime = MagicMock()
        my_runtime.service.return_value.get_current_user.return_value.opt_attrs.get.return_value = "student audit"
        self.runtime = my_runtime

    def get_children(self):
        return self.children


@override_settings(SUMMARY_HOOK_MIN_SIZE=40,
                   SUMMARY_HOOK_HOST='http://hookhost',
                   SUMMARY_HOOK_JS_PATH='/jspath',
                   HTML_TAGS_TO_REMOVE=['script', 'style', 'test'])
class TestSummaryHookAside(TestCase):
    """Summary hook aside tests"""
    def setUp(self):
        transcript_utils_mock = MagicMock()
        transcript_utils_mock.get_transcript = fake_get_transcript

        xmodule_exceptions_mock = MagicMock()
        xmodule_exceptions_mock.NotFoundError = MagicMock()

        modules = {
            'xmodule.exceptions': xmodule_exceptions_mock,
            'xmodule.video_block.transcripts_utils': transcript_utils_mock,
        }

        patch.dict('sys.modules', modules).start()

    def test_format_date(self):
        formatted_date = _format_date(date1)
        self.assertEqual(formatted_date, '2023-01-02T03:04:05')

    def test_format_date_with_invalid_input(self):
        invalid_date = '2023-05-01'
        formatted_date = _format_date(invalid_date)
        self.assertIsNone(formatted_date)

    def test_extract_child_contents_with_html(self):
        category = 'html'

        child = FakeChild(category)
        content = _extract_child_contents(child, category)

        self.assertEqual(content, 'This is a test')

    def test_extract_child_contents_with_video(self):
        category = 'video'

        child = FakeChild(category)
        content = _extract_child_contents(child, category)
        self.assertEqual(content, 'This is the text version from the transcript')

    def test_extract_child_contents_with_invalid_category(self):
        category = 'invalid'

        child = FakeChild(category)
        content = _extract_child_contents(child, category)
        self.assertIsNone(content)

    def test_check_summarizable_with_valid_children(self):
        children = [
            FakeChild('html', '01', '''
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Vivamus dapibus elit lacus, at vehicula arcu vehicula in.
                    In id felis arcu. Maecenas elit quam, volutpat cursus pharetra vel, tempor at lorem.
                    Fusce luctus orci quis tempor aliquet.
                </p>'''),
            FakeChild('html', '02', '''
                <Everything on the content on this child is inside a tag, so parsing it would return almost>
                    Nothing
                </The quick brown fox jumps over the lazy dog>'''),
            FakeChild('video', '03'),
            FakeChild('unknown', '04'),
        ]
        block = FakeBlock(children)

        content = _check_summarizable(block)

        self.assertTrue(content)

    def test_check_summarizable_with_invalid_children(self):
        children = [
            FakeChild('html', '01', '<p>Test</p>'),
            FakeChild('unknown', '04'),
        ]
        block = FakeBlock(children)

        content = _check_summarizable(block)

        self.assertFalse(content)

    def test_parse_children_contents_with_valid_children(self):
        children = [
            FakeChild('html', '01', '''
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Vivamus dapibus elit lacus, at vehicula arcu vehicula in.
                    In id felis arcu. Maecenas elit quam, volutpat cursus pharetra vel, tempor at lorem.
                    Fusce luctus orci quis tempor aliquet.
                </p>'''),
            FakeChild('html', '02', '''
                <Everything on the content on this child is inside a tag, so parsing it would return almost>
                    Nothing
                </The quick brown fox jumps over the lazy dog>'''),
            FakeChild('video', '03'),
            FakeChild('unknown', '04'),
        ]
        block = FakeBlock(children)

        expected_length, expected_items = (
            289,
            [{
                'definition_id': 'def-id-01',
                'content_type': 'TEXT',
                'content_text': dedent('''\
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Vivamus dapibus elit lacus, at vehicula arcu vehicula in.
                    In id felis arcu. Maecenas elit quam, volutpat cursus pharetra vel, tempor at lorem.
                    Fusce luctus orci quis tempor aliquet.'''),
                'published_on': 'published-on-01',
                'edited_on': 'edited-on-01',
            }, {
                'definition_id': 'def-id-02',
                'content_type': 'TEXT',
                'content_text': 'Nothing',
                'published_on': 'published-on-02',
                'edited_on': 'edited-on-02',
            }, {
                'definition_id': 'def-id-03',
                'content_type': 'VIDEO',
                'content_text': fake_transcript,
                'published_on': 'published-on-03',
                'edited_on': 'edited-on-03',
            }]
        )

        length, items = _parse_children_contents(block)

        self.assertEqual(length, expected_length)
        self.assertEqual(items, expected_items)

    def test_parse_children_contents_with_valid_children_2(self):
        children = [
            FakeChild('html', '01', '''
                <p>
                    Lorem ipsum.
                </p>'''),
            FakeChild('html', '02', '''
                <Everything on the content on this child is inside a tag, so parsing it would return almost>
                    Nothing
                </The quick brown fox jumps over the lazy dog>'''),
            FakeChild('unknown', '03'),
        ]
        block = FakeBlock(children)

        expected_length, expected_items = (
            19,
            [{
                'definition_id': 'def-id-01',
                'content_type': 'TEXT',
                'content_text': 'Lorem ipsum.',
                'published_on': 'published-on-01',
                'edited_on': 'edited-on-01',
            }, {
                'definition_id': 'def-id-02',
                'content_type': 'TEXT',
                'content_text': 'Nothing',
                'published_on': 'published-on-02',
                'edited_on': 'edited-on-02',
            }]
        )

        length, items = _parse_children_contents(block)
        self.assertEqual(length, expected_length)
        self.assertEqual(items, expected_items)

    def test_parse_children_contents_with_script_or_style_tags(self):
        children = [
            FakeChild('html', '01', '''
                <span>This should be the only text to be extracted.</span>
                <test>For testing purposes only, this tag is ignored as well</test>
                <script>
                  function ignore() {
                    console.log('This content should be ignored.');
                  }
                </script>
                <script type="text/javascript">
                  console.log('This should be ignored as well.')
                </script>
                <script src="https://nevermind.me/i-should-also-be-discarded.js" type="text/javascript"></script>'''),
            FakeChild('html', '02', '''
                <div class="cypher">Why oh why didn't I take the <em>BLUE</em> pill?</div>
                <style>
                  .cypher em {
                    color: #00f;
                  }
                </style>'''),
        ]
        block = FakeBlock(children)

        expected_length, expected_items = (
            84,
            [{
                'definition_id': 'def-id-01',
                'content_type': 'TEXT',
                'content_text': 'This should be the only text to be extracted.',
                'published_on': 'published-on-01',
                'edited_on': 'edited-on-01',
            }, {
                'definition_id': 'def-id-02',
                'content_type': 'TEXT',
                'content_text': 'Why oh why didn\'t I take the BLUE pill?',
                'published_on': 'published-on-02',
                'edited_on': 'edited-on-02',
            }]
        )

        length, items = _parse_children_contents(block)

        self.assertEqual(length, expected_length)
        self.assertEqual(items, expected_items)

    def test_parse_children_contents_with_invalid_children(self):
        children = [
            FakeChild('html', '01', '<div>This</div>'),
            FakeChild('unknown', '03', '<div>This will not be parsed, category: <em>unknown</em>.<p>'),
        ]
        block = FakeBlock(children)

        length, items = _parse_children_contents(block)

        self.assertEqual(length, 0)
        self.assertEqual(items, [])

    def test_render_hook_fragment(self):
        block = FakeBlock([])
        items = [{
            'published_on': date1,
            'edited_on': date1,
        }, {
            'published_on': date2,
            'edited_on': date1,
        }]
        expected = '''
        <div>&nbsp;</div>
          <div class="summary-hook">
            <div summary-launch>
                <div id="launch-summary-button"
                data-url-api="http://hookhost"
                data-course-id="course-v1:edX+A+B"
                data-content-id="block-v1:edX+A+B+type@vertical+block@verticalD"
                data-handler-url="http://handler.url"
                data-last-updated="2023-06-07T08:09:10"
                data-user-role="user role string"
                >
                </div>
            </div>
            <div id="ai-spot-root"></div>
            <script type="text/javascript" src="http://hookhost/jspath" defer="defer"></script>
        </div>
        '''
        fragment = _render_hook_fragment('user role string', 'http://handler.url', block, items)
        self.assertEqual(
            # join and split to ignore whitespace differences
            "".join(fragment.body_html()).split(),
            "".join(expected).split()
        )

    def test_user_role_from_services(self):
        user_service = Mock()
        credit_service = Mock()
        user = Mock()
        enrollment = Mock()

        user_service.get_current_user.return_value = user
        user.opt_attrs.get.return_value = 'the_user_role'
        credit_service.get_credit_state.return_value = enrollment
        enrollment.get.return_value = 'the_enrollment_mode'

        expected_role = 'the_user_role the_enrollment_mode'
        # pylint: disable=protected-access
        returned_role = SummaryHookAside._user_role_string_from_services(user_service, credit_service, "course_key")
        self.assertEqual(returned_role, expected_role)

        self.assertEqual(credit_service.mock_calls,
                         [call.get_credit_state('the_user_role', 'course_key'),
                          call.get_credit_state().get('enrollment_mode'),
                          call.get_credit_state().get('enrollment_mode')])

        user_service.get_current_user.return_value = None
        expected_role = 'unknown'
        # pylint: disable=protected-access
        returned_role = SummaryHookAside._user_role_string_from_services(user_service, credit_service, "course_key")
        self.assertEqual(returned_role, expected_role)

    def test_user_role_with_no_enrollment(self):
        user_service = Mock()
        credit_service = Mock()
        user = Mock()
        enrollment = None

        user_service.get_current_user.return_value = user
        credit_service.get_credit_state.return_value = enrollment
        user.opt_attrs.get.return_value = 'the role'

        expected_role = 'the role'
        # pylint: disable=protected-access
        returned_role = SummaryHookAside._user_role_string_from_services(user_service, credit_service, "course_key")
        self.assertEqual(returned_role, expected_role)


@override_settings(SUMMARY_HOOK_MIN_SIZE=40, HTML_TAGS_TO_REMOVE=['script', 'style', 'test'])
class TestSummaryHookAsideMissingTranscript(TestCase):
    """Summary hook aside tests for the case where a transcript is missing"""
    def setUp(self):
        class FakeNotFoundError(BaseException):
            pass

        xmodule_exceptions_mock = MagicMock()
        xmodule_exceptions_mock.NotFoundError = FakeNotFoundError

        def error_get_transcript(child, lang=None, output_format='SRT',
                                 youtube_id=None):
            raise FakeNotFoundError()

        transcript_utils_mock = MagicMock()
        transcript_utils_mock.get_transcript = error_get_transcript

        modules = {
            'xmodule.exceptions': xmodule_exceptions_mock,
            'xmodule.video_block.transcripts_utils': transcript_utils_mock,
        }

        patch.dict('sys.modules', modules).start()

    def test_extract_child_contents_with_broken_video(self):
        category = 'video'

        child = FakeChild(category)
        content = _extract_child_contents(child, category)
        self.assertEqual(content, None)

    def test_parse_children_contents_with_partly_valid_children(self):
        children = [
            FakeChild('html', '01', '''
                <p>
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Vivamus dapibus elit lacus, at vehicula arcu vehicula in.
                    In id felis arcu. Maecenas elit quam, volutpat cursus pharetra vel, tempor at lorem.
                    Fusce luctus orci quis tempor aliquet.
                </p>'''),
            FakeChild('html', '02', '''
                <Everything on the content on this child is inside a tag, so parsing it would return almost>
                    Nothing
                </The quick brown fox jumps over the lazy dog>'''),
            FakeChild('video', '03'),
            FakeChild('unknown', '04'),
        ]
        block = FakeBlock(children)

        expected_length, expected_items = (
            245,
            [{
                'definition_id': 'def-id-01',
                'content_type': 'TEXT',
                'content_text': dedent('''\
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                    Vivamus dapibus elit lacus, at vehicula arcu vehicula in.
                    In id felis arcu. Maecenas elit quam, volutpat cursus pharetra vel, tempor at lorem.
                    Fusce luctus orci quis tempor aliquet.'''),
                'published_on': 'published-on-01',
                'edited_on': 'edited-on-01',
            }, {
                'definition_id': 'def-id-02',
                'content_type': 'TEXT',
                'content_text': 'Nothing',
                'published_on': 'published-on-02',
                'edited_on': 'edited-on-02',
            }]
        )

        length, items = _parse_children_contents(block)

        self.assertEqual(length, expected_length)
        self.assertEqual(items, expected_items)


if __name__ == '__main__':
    unittest.main()
