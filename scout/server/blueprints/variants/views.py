# -*- coding: utf-8 -*-
from flask import Blueprint, request

from scout.constants import SEVERE_SO_TERMS
from scout.server.extensions import store
from scout.server.utils import templated, institute_and_case
from . import controllers
from .forms import FiltersForm

variants_bp = Blueprint('variants', __name__, template_folder='templates')


@variants_bp.route('/<institute_id>/<case_name>/variants')
@templated('variants/variants.html')
def variants(institute_id, case_name):
    """Display a list of SNV variants."""
    variant_type = request.args['variant_type']
    page = int(request.args.get('page', 1))
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    form = FiltersForm(request.args)
    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in case_obj.get('panels', [])]
    form.gene_panels.choices = panel_choices

    variants_query = store.variants(case_obj['_id'], query=form.data)
    data = controllers.variants(store, variants_query, page)

    return dict(institute=institute_obj, case=case_obj, variant_type=variant_type,
                form=form, severe_so_terms=SEVERE_SO_TERMS, page=page, **data)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>')
@templated('variants/variant.html')
def variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    return dict(institute=institute_obj, case=case_obj, variant=variant_obj)


@variants_bp.route('/<institute_id>/<case_name>/sv/variants')
@templated('variants/sv-variants.html')
def sv_variants(institute_id, case_name):
    """Display a list of structural variants."""
    return dict()


@variants_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variants/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    return dict()
