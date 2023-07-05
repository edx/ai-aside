"""
Text manipulation utils.
"""

from html.parser import HTMLParser
from re import sub

from django.conf import settings


def cleanup_text(text):
    """
    Removes litter from replacing or manipulating text
    """
    stripped = sub(r'[^\S\r\n]+', ' ', text)  # Removing extra spaces
    stripped = sub(r'\n{2,}', '\n', stripped)  # Removing extra new lines
    stripped = sub(r'(\s+)?\n(\s+)?', '\n', stripped)  # Removing starting extra spacesbetween new lines
    stripped = sub(r'(^(\s+)\n?)|(\n(\s+)?$)', '', stripped)  # Trim

    return stripped


class _HTMLToTextHelper(HTMLParser):  # lint-amnesty, pylint: disable=abstract-method
    """
    Helper function for html_to_text below
    """
    _is_content = True

    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_starttag(self, tag, _):
        """This runs when a new tag is found. We use this to exclude unwanted content."""
        tags_to_filter = getattr(settings, 'HTML_TAGS_TO_REMOVE', None)
        self._is_content = not (tags_to_filter and tag in tags_to_filter)

    def handle_data(self, data):
        """takes the data in separate chunks"""
        if self._is_content:
            self.fed.append(data)

    def handle_entityref(self, name):
        """appends the reference to the body"""
        if self._is_content:
            self.fed.append('&%s;' % name)

    def get_data(self):
        """joins together the seperate chunks into one cohesive string"""
        return ''.join(self.fed)


def html_to_text(html):
    """
    Strips the html tags off of the text to return plaintext
    """

    htmlstripper = _HTMLToTextHelper()
    htmlstripper.feed(html)
    text = htmlstripper.get_data()
    text = cleanup_text(text)

    return text
