# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import os
import io
import json

from flask import Blueprint, current_app

from ...decorators import templated

core = Blueprint('core', __name__, template_folder='templates')


@core.route('/cases')
@templated('cases.html')
def cases():
  """View all cases."""
  # fetch variants from the data store
  project_root = '/'.join(current_app.root_path.split('/')[0:-1])
  data_path = os.path.join(project_root, 'tests/fixtures/variants.json')
  with io.open(data_path, encoding='utf-8') as handle:
    variants = json.load(handle)

  return dict(variants=variants)
