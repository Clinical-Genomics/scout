# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import abort, flash
from mongoengine import DoesNotExist

from scout.extensions import store


def validate_user(current_user, institute_id):
  # abort with 404 error if case/institute doesn't exist
  try:
    institute = store.institute(institute_id)
  except DoesNotExist as exception:
    return abort(404)

  if institute not in current_user.institutes:
    flash('You do not have access to this institute.')
    return abort(403)

  return institute
