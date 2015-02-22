# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import abort, flash

from ..helpers import get_document_or_404
from ..models import Institute


def validate_user(current_user, institute_id):
  # abort with 404 error if case/institute doesn't exist
  institute = get_document_or_404(Institute, institute_id)

  if institute not in current_user.institutes:
    flash('You do not have access to this institute.')
    return abort(403)

  return institute
