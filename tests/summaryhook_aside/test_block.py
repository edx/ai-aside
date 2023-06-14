import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from ai_aside.summaryhook_aside.block import _extract_child_contents, _format_date, _get_children_contents


class FakeTranscript():
    def convert(transcript, format, output):
        return 'This is the text version from the transcript'


def fake_get_transcript(child):
    return ['This is a transcript']


class FakeChild:
    transcript_download_format = 'txt'

    def __init__(self, category, test_id='test-id'):
        self.category = category
        self.published_on = 'published-on-{}'.format(test_id)
        self.edited_on = 'edited-on-{}'.format(test_id)
        self.scope_ids = lambda: None
        self.scope_ids.def_id = 'def-id-{}'.format(test_id)

    def get_html(self):
        if self.category == 'html':
            return '<div>This is a test</div>'

        return None


class FakeBlock:
    def __init__(self, children):
        self.children = children

    def get_children(self):
        return self.children


class TestSummaryHookAside(unittest.TestCase):
    def setUp(self):
        module_mock = MagicMock()
        module_mock.Transcript = FakeTranscript
        module_mock.get_transcript = fake_get_transcript
        modules = {'xmodule.video_block.transcripts_utils': module_mock}
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

    def test_get_children_contents_with_valid_children(self):
        children = [
            FakeChild('html', '01'),
            FakeChild('video', '02'),
            FakeChild('unknown', '03'),
        ]
        block = FakeBlock(children)

        expected = [{
            'definition_id': 'def-id-01',
            'type': 'TEXT',
            'text': 'This is a test',
            'published_on': 'published-on-01',
            'edited_on': 'edited-on-01',
        }, {
            'definition_id': 'def-id-02',
            'type': 'VIDEO',
            'text': 'This is the text version from the transcript',
            'published_on': 'published-on-02',
            'edited_on': 'edited-on-02',
        }]

        content = _get_children_contents(block)

        self.assertEqual(content, expected)


if __name__ == '__main__':
    unittest.main()
