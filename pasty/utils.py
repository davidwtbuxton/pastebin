import functools
import io
import itertools
import string

import pygments
from django.core.exceptions import PermissionDenied
from google.appengine.api import users
from pygments import formatters
from pygments import lexers
from pygments import styles
from pygments.util import ClassNotFound


PYGMENTS_STYLE = 'autumn'


def get_current_user_email():
    user = users.get_current_user()

    return user.email() if user else u''


def admin_required(view_func):
    @functools.wraps(view_func)
    def _func(request, *args, **kwargs):
        if users.is_current_user_admin():
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied

    return _func


def get_language_names():
    """Returns a sorted list of the syntaxes supported for highlighting."""
    names = [name for name, aliases, ftypes, mtypes in lexers.get_all_lexers()]
    names.sort(key=lambda x: x.lower())

    return names


def highlight_content(content, language=None, filename=None):
    """Applies code highlighting and returns the markup. If language or filename
    is None then the language is guessed from the content.
    """
    lexer = None

    if language:
        try:
            lexer = lexers.get_lexer_by_name(language)
        except ClassNotFound:
            pass

    if filename:
        try:
            lexer = lexers.get_lexer_for_filename(filename)
        except ClassNotFound:
            pass

    if not lexer:
        try:
            lexer = lexers.guess_lexer(content)
        except ClassNotFound:
            # No match by language or filename, and Pygments can't guess what
            # it is. So let's treat it as plain text.
            lexer = lexers.get_lexer_by_name('text')

    style_class = highlight_css[PYGMENTS_STYLE][0]
    cssclass = 'highlight ' + style_class
    formatter = formatters.HtmlFormatter(style=PYGMENTS_STYLE, cssclass=cssclass)
    highlighted = pygments.highlight(content, lexer, formatter)

    return highlighted


def summarize_content(content, language=None, filename=None):
    """Returns a summary of the content, with syntax highlighting."""
    lines = 10
    summary = u'\n'.join(content.strip().splitlines()[:lines]).strip()
    summary = highlight_content(summary, language=language)

    return summary


def get_all_highlight_css():
    """Yields pairs of (<name>, <css-string>) for every Pygment HTML style."""
    for name in styles.get_all_styles():
        cssclass = 'highlight__' + name
        formatter = formatters.HtmlFormatter(style=name, cssclass=cssclass)
        css = formatter.get_style_defs()
        css = (u'/* Pygment\'s %s style. */\n' % name) + css

        yield (name, cssclass, css)


#: Mapping of {<style-name>: (<class-name>, <css>)}.
highlight_css = {name: (klass, style) for name, klass, style in get_all_highlight_css()}


def highlight_styles():
    """Returns the syntax highlighting CSS as an encoded string."""
    content = u'\n\n'.join(css for _, css in highlight_css.values())
    content = content.encode('utf-8')

    return content


def get_url_patterns(prefix=None):
    """Returns a list of url definitions, optionally filtered by patterns
    matching the prefix.

    Each item is a pair of (name, pattern).
    """
    return []


def count_lines(content):
    """Returns the number of lines for a string."""
    try:
        fh = io.StringIO(content)
    except TypeError:
        fh = io.BytesIO(content)

    count = 0

    for count, _ in enumerate(fh, 1):
        pass

    return count


def untitled_name_generator():
    """Returns a generator which yields strings like 'untitled.txt',
    'untitled-2.txt', 'untitled-3.txt'.
    """
    counter = itertools.count(1)
    name = 'untitled%s.txt'

    while True:
        n = next(counter)
        suffix = '' if n == 1 else ('-' + int(n))

        yield name % suffix


class BaseConverter(object):
    def __init__(self, digits):
        self.digits = digits
        self.base = len(digits)

    def encode(self, value):
        base, digits = self.base, self.digits

        if value < 0:
            sign = '-'
            value = abs(value)
        else:
            sign = ''

        value, rem = divmod(value, base)
        chars = [digits[rem]]

        while value:
            value, rem = divmod(value, base)
            chars.append(digits[rem])

        return sign + ''.join(reversed(chars))

    def decode(self, value):
        base, digits = self.base, self.digits

        if value.startswith('-'):
            sign = -1
            value = value[1:]
        else:
            sign = 1

        result = 0

        for power, char in enumerate(reversed(value)):
            pos = digits.index(char)
            result += (base ** power) * pos

        return result * sign


base62 = BaseConverter(string.digits + string.ascii_uppercase + string.ascii_lowercase)
