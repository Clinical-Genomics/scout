# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint, current_app

from ...decorators import templated

core = Blueprint('core', __name__, template_folder='templates')


@core.route('/cases')
@templated('cases.html')
def cases():
  """View all cases.

  The purpose of this page is to display all cases related to an
  institute. It should also give an idea of which
  """
  # fetch cases from the data store
  return dict(cases=current_app.db.cases())


@core.route('/cases/<case_id>')
@templated('case.html')
def case(case_id):
  """View one specific case."""
  # fetch a single, specific case from the data store
  return dict(case=current_app.db.case(case_id))


@core.route('/<case_id>/variants')
@templated('variants.html')
def variants(case_id):
  """View all variants for a single case."""
  # fetch all variants for a specific case
  return dict(variants=current_app.db.variants(case_id), case_id=case_id)


@core.route('/<case_id>/variants/<variant_id>')
@templated('variant.html')
def variant(case_id, variant_id):
  """View a single variant in a single case."""
  return dict(variant=current_app.db.variant(variant_id, case_id=case_id),
              case_id=case_id)
