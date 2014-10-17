# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, current_app

from ...decorators import templated

core = Blueprint('core', __name__, template_folder='templates')


@core.route('/families')
@templated('families.html')
def families():
  """View all families."""
  # fetch families from the data store
  return dict(families=current_app.db.families())
