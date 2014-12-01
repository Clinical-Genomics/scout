# -*- coding: utf-8 -*-
from functools import wraps
import hashlib

from flask import abort, request, render_template
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
