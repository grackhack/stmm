from unittest import TestCase

from webparser import websettings
from webparser.seleniumparser import WebParser

class TestWebParser(TestCase):
    def test_print_source(self):
        with WebParser('https://www.myscore.ru/') as w:
                self.assertIn(websettings.MSC_MAIN_TABLE, w.get_source_html(), 'Page not contain main table')

