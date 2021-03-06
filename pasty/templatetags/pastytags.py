import datetime

from django import template
from django.template import defaultfilters


register = template.Library()


@register.simple_tag
def render_label(bound_field, **kwargs):
    """Helper to render a form field label, adding attributes to the element."""
    markup = bound_field.label_tag(attrs=kwargs)

    return markup


@register.simple_tag
def render_input(bound_field, **kwargs):
    """Helper to render a form field input, adding attributes to the element."""
    # This logic is copied from BoundField.__str__.
    markup = bound_field.as_widget(attrs=kwargs)

    if bound_field.field.show_hidden_initial:
        markup = markup + bound_field.as_hidden(only_initial=True)

    return markup


def _since(dt, moment):
    """Returns the time since for a date, like '1 year' or '12 hours'."""
    one_day = 3600 * 24

    # Bit silly having months and years since the filter is hard-coded to only
    # use this for datetimes less than 2 days old.
    periods = [
        (one_day * 365, u'year', u'years'),
        (one_day * 28, u'month', u'months'),
        (one_day, u'day', u'days'),
        (3600, u'hour', 'hours'),
        (60, u'minute', u'minutes'),
        (1, u'second', u'seconds'),
    ]

    delta = moment - dt
    delta_seconds = delta.total_seconds()

    for period, singular, plural in periods:
        num =  delta_seconds // period

        if num:
            form = singular if num == 1 else plural

            return u'%d %s' % (num, form)
    else:
        return u'0 seconds'


@register.filter
def since(dt, arg=None):
    moment = datetime.datetime.utcnow()
    delta = datetime.timedelta(days=2)

    # Only do fancy things if it's younger than delta.
    if (moment - dt) < delta:
        return _since(dt, moment) + u' ago'

    else:
        return defaultfilters.date(dt, arg=arg)


@register.simple_tag
def params(qdict, **kwargs):
    """Helper for building a query string, adding and removing params to
    an existing query dict.

    In a template, use it like:

    {% params request.GET page=4 %}
    """
    qdict = qdict.copy()

    for name, value in kwargs.items():
        if value is None:
            if name in qdict:
                del qdict[name]
        else:
            qdict[name] = value

    return qdict.urlencode()
