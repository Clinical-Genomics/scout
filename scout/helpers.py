# -*- coding: utf-8 -*-
from functools import wraps
import hashlib

import mimetypes
import os
import re

from flask import abort, render_template, request, Response, send_file
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
      context = f(*args, **kwargs)
      if context is None:
        context = {}
      elif not isinstance(context, dict):
        return context
      return render_template(template_name, **context)
    return decorated_function
  return decorator


def md5ify(list_of_arguments):
  """Generate an md5-key from a list of arguments"""
  hash_key = hashlib.md5()
  hash_key.update(' '.join(list_of_arguments))
  return hash_key.hexdigest()


def get_document_or_404(model, **filters):
  """Fetch a document from the database or return a 404 unless found."""
  try:
    return model.objects.get(**filters)
  except DoesNotExist:
    return abort(404)
