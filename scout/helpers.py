# -*- coding: utf-8 -*-
from datetime import datetime
from functools import wraps
import hashlib

from flask import request, render_template
from mongoengine import DoesNotExist


def templated(template=None):
  """Template decorator.

  Ref: http://flask.pocoo.org/docs/patterns/viewdecorators/
  """
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      template_name = template
      if template_name is None:
        template_name = request.endpoint.replace('.', '/') + '.html'
      ctx = f(*args, **kwargs)
      if ctx is None:
        ctx = {}
      elif not isinstance(ctx, dict):
        return ctx
      return render_template(template_name, **ctx)
    return decorated_function
  return decorator


def pretty_date(date, default=None):
  """Return string representing "time since": 3 days ago, 5 hours ago.
  Ref: https://bitbucket.org/danjac/newsmeme/src/a281babb9ca3/newsmeme/
  """
  if default is None:
    default = 'just now'

  now = datetime.utcnow()
  diff = now - date

  periods = (
    (diff.days / 365, 'year', 'years'),
    (diff.days / 30, 'month', 'months'),
    (diff.days / 7, 'week', 'weeks'),
    (diff.days, 'day', 'days'),
    (diff.seconds / 3600, 'hour', 'hours'),
    (diff.seconds / 60, 'minute', 'minutes'),
    (diff.seconds, 'second', 'seconds'),
  )

  for period, singular, plural in periods:

    if not period:
      continue

    if period == 1:
      return "%d %s ago" % (period, singular)
    else:
      return "%d %s ago" % (period, plural)

  return default


def md5ify(list_of_arguments):
  """Generate an md5-key from a list of arguments"""
  h = hashlib.md5()
  h.update(' '.join(list_of_arguments))
  return h.hexdigest()


def get_document_or_404(model, display_name):
  try:
    return model.objects.get(display_name=display_name)
  except DoesNotExist:
    return abort(404)
