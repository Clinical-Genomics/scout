# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from flask import Blueprint
from flask.ext.login import login_required

from ..extensions import store
from ..helpers import templated

core = Blueprint('core', __name__, template_folder='templates')


@core.route('/cases')
@templated('cases.html')
@login_required
def cases():
  """View all cases.

  The purpose of this page is to display all cases related to an
  institute. It should also give an idea of which
  """
  # fetch cases from the data store
  return dict(cases=store.cases())


@core.route('/cases/<case_id>')
@templated('case.html')
@login_required
def case(case_id):
  """View one specific case."""
  # fetch a single, specific case from the data store
  return dict(case=store.case(case_id))


@core.route('/<case_id>/variants')
@templated('variants.html')
@login_required
def variants(case_id):
  """View all variants for a single case."""
  # fetch all variants for a specific case
  return dict(variants=store.variants(case_id), case_id=case_id)


@core.route('/<case_id>/variants/<variant_id>')
@templated('variant.html')
@login_required
def variant(case_id, variant_id):
  """View a single variant in a single case."""
  return dict(variant=store.variant(variant_id, case_id=case_id),
              case_id=case_id)
