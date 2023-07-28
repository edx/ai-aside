"""Tests for the block."""
import unittest
from datetime import datetime
from textwrap import dedent
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from ai_aside.block import _check_summarizable, _extract_child_contents, _format_date, _parse_children_contents

fake_transcript = 'This is the text version from the transcript'


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

    def get_children(self):
        return self.children


@override_settings(SUMMARY_HOOK_MIN_SIZE=40, HTML_TAGS_TO_REMOVE=['script', 'style', 'test'])
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
        date = datetime(2023, 5, 1, 12, 0, 0)
        formatted_date = _format_date(date)
        self.assertEqual(formatted_date, '2023-05-01 12:00:00')

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
