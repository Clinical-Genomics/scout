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


def get_document_or_404(model, display_name):
  """Fetch a document from the database or return a 404 unless found."""
  try:
    return model.objects.get(display_name=display_name)
  except DoesNotExist:
    return abort(404)


def send_file_partial(path):
  """Simple wrapper around send_file which handles HTTP 206 Partial
  Content (byte ranges).

  TODO: handle all send_file args, mirror send_file's error handling
  (if it has any)."""
  range_header = request.headers.get('Range', None)
  if not range_header:
    return send_file(path)

  size = os.path.getsize(path)
  byte1, byte2 = 0, None

  match = re.search('(\d+)-(\d*)', range_header)
  groups = match.groups()

  if groups[0]:
    byte1 = int(groups[0])
  if groups[1]:
    byte2 = int(groups[1])

  length = size - byte1
  if byte2 is not None:
    length = byte2 - byte1

  data = None
  with open(path, 'rb') as handle:
    handle.seek(byte1)
    data = handle.read(length)

  resp = Response(data, 206, mimetype=mimetypes.guess_type(path)[0],
                  direct_passthrough=True)

  resp.headers.add('Content-Range',
                   "bytes {0}-{1}/{2}".format(byte1, byte1 + length - 1, size))

  return resp
