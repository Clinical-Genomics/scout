# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, current_app

from ...decorators import templated

core = Blueprint('core', __name__, template_folder='templates')


@core.route('/cases')
@templated('cases.html')
def cases():
  """View all cases."""
  # fetch cases from the data store
  return dict(cases=current_app.db.cases())
