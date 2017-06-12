from django.http import Http404

from . import AppEngineTestCase
from pasty.models import Paste, PastyFile


class PasteTestCase(AppEngineTestCase):
    def test_unicode(self):
        obj = Paste(author='alice@example.com', filename='example.txt')

        self.assertEqual(unicode(obj), u'alice@example.com / example.txt')

    def test_unicode_for_anonymous_author(self):
        obj = Paste(filename='example.txt')

        self.assertEqual(unicode(obj), u'anonymous / example.txt')

    def test_get_or_404_with_none_id(self):
        with self.assertRaises(Http404):
            Paste.get_or_404(None)

    def test_get_or_404_with_bad_id(self):
        with self.assertRaises(Http404):
            Paste.get_or_404('bogus')

    def test_get_or_404_with_unknown_id(self):
        self.assertIsNone(Paste.get_by_id(1234))

        with self.assertRaises(Http404):
            Paste.get_or_404(1234)

    def test_get_or_404_returns_paste_for_valid_integer_id(self):
        Paste(id=1234).put()

        obj = Paste.get_or_404(1234)

        self.assertEqual(obj.key.id(), 1234)

    def test_get_or_404_returns_paste_for_valid_string_id(self):
        Paste(id=1234).put()

        obj = Paste.get_or_404('1234')

        self.assertEqual(obj.key.id(), 1234)


class PastyFileTestCase(AppEngineTestCase):
    def test_default_content_type(self):
        obj = PastyFile()

        self.assertEqual(obj.content_type, 'text/plain')

    def test_known_content_type(self):
        obj = PastyFile(filename='example.jpg')

        self.assertEqual(obj.content_type, 'image/jpeg')
