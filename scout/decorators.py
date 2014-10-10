# -*- coding: utf-8 -*-
from functools import wraps

from flask import request, render_template


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
