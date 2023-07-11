"""Tests for text utils used by the blocks"""
import unittest
from textwrap import dedent

from ai_aside.text_utils import html_to_text


class TestSummaryHookAside(unittest.TestCase):
    """Tests of text utils as used by the summary hook"""
    def test_html_to_text(self):
        html_content = '''\
            <div>
                <h1>Lorem Ipsum</h1>
                <p>Lorem ipsum dolor <em style="font-size: 99pt;">sit amet</em>, consectetur adipiscing elit.</p>
                <!-- The next paragraph will have an intentional mismatching close tag -->
                <p>Sed volutpat velit sed dui <i class="something">fringilla</i> fermentum.</div>
                <p>Nullam quis velit at turpis lacinia convallis.</p>
            </div>'''
        expected_text = dedent('''\
            Lorem Ipsum
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            Sed volutpat velit sed dui fringilla fermentum.
            Nullam quis velit at turpis lacinia convallis.''')
        text = html_to_text(html_content)
        self.assertEqual(text, expected_text)

    def test_html_to_text_messy(self):
        html_content = '''\
            <custom>
                <mismatching>Lorem Ipsum</tags>
                > Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                > Sed volutpat velit sed dui fringilla fermentum.</42>
                <p>> Nullam quis velit at turpis lacinia convallis.</p>'''
        expected_text = dedent('''\
            Lorem Ipsum
            > Lorem ipsum dolor sit amet, consectetur adipiscing elit.
            > Sed volutpat velit sed dui fringilla fermentum.
            > Nullam quis velit at turpis lacinia convallis.''')
        text = html_to_text(html_content)
        self.assertEqual(text, expected_text)

    def test_html_to_text_iframe(self):
        html_content = '''\
            <iframe
                src="https://mitx.qualtrics.com/jfe/form/SV_8ocnXlmaDwMRFgF?user_id=%%USER_ID%%"
                height="1200"
                width="100%"
                title="Nothing useful can be parsed from this, maybe fetching the src in the future?"
            ></iframe>
            '''
        expected_text = dedent('')
        text = html_to_text(html_content)
        self.assertEqual(text, expected_text)


if __name__ == '__main__':
    unittest.main()
