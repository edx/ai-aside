import unittest
from datetime import datetime

from django.conf import settings

from ai_aside.summaryhook_aside.block import _extract_child_contents, _format_date, _html_to_text_fallback


class TestSummaryHookAside(unittest.TestCase):
    def test_format_date(self):
        date = datetime(2023, 5, 1, 12, 0, 0)
        formatted_date = _format_date(date)
        self.assertEqual(formatted_date, '2023-05-01 12:00:00')

    def test_format_date_with_invalid_input(self):
        invalid_date = '2023-05-01'
        formatted_date = _format_date(invalid_date)
        self.assertIsNone(formatted_date)

    def test_html_to_text_fallback(self):
        html_content = '<p>This is <b>bold</b> text.</p>'
        text = _html_to_text_fallback(html_content)
        self.assertEqual(text, 'This is bold text.')

    def test_extract_child_contents_with_invalid_category(self):
        class Child:
            def __init__(self):
                self.category = 'invalid'

        child = Child()
        content = _extract_child_contents(child, 'invalid')
        self.assertIsNone(content)


if __name__ == '__main__':
    unittest.main()
