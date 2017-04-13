# -*- coding: utf-8 -*-
import logging

from flask import Blueprint, request, redirect, abort, flash, current_app
from flask_login import current_user

from scout.constants import SEVERE_SO_TERMS
from scout.server.extensions import store, mail, loqusdb
from scout.server.utils import templated, institute_and_case
from . import controllers
from .forms import FiltersForm, SvFiltersForm

log = logging.getLogger(__name__)
variants_bp = Blueprint('variants', __name__, template_folder='templates')


@variants_bp.route('/<institute_id>/<case_name>/variants')
@templated('variants/variants.html')
def variants(institute_id, case_name):
    """Display a list of SNV variants."""
    page = int(request.args.get('page', 1))
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    form = FiltersForm(request.args)
    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in case_obj.get('panels', [])]
    form.gene_panels.choices = panel_choices

    # handle HPO gene list separately
    if form.data['gene_panels'] == ['hpo']:
        hpo_symbols = list(set(term_obj['hgnc_symbol'] for term_obj in
                               case_obj['dynamic_gene_list']))
        form.hgnc_symbols.data = hpo_symbols

    variants_query = store.variants(case_obj['_id'], query=form.data)
    data = controllers.variants(store, variants_query, page)

    return dict(institute=institute_obj, case=case_obj, form=form,
                severe_so_terms=SEVERE_SO_TERMS, page=page, **data)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>')
@templated('variants/variant.html')
def variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    controllers.variant_case(case_obj)
    data = controllers.variant(store, institute_obj, case_obj, variant_id)
    if data is None:
        return abort(404)
    if current_app.config.get('LOQUSDB_SETTINGS'):
        data['observations'] = controllers.observations(loqusdb, data['variant'])
    return dict(institute=institute_obj, case=case_obj, **data)


@variants_bp.route('/<institute_id>/<case_name>/sv/variants')
@templated('variants/sv-variants.html')
def sv_variants(institute_id, case_name):
    """Display a list of structural variants."""
    page = int(request.args.get('page', 1))
    variant_type = request.args.get('variant_type', 'clinical')

    form = SvFiltersForm(request.args)

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    panel_choices = [(panel['panel_name'], panel['display_name'])
                     for panel in case_obj.get('panels', [])]
    form.gene_panels.choices = panel_choices
    query = form.data
    query['variant_type'] = variant_type
    variants_query = store.variants(case_obj['_id'], category='sv', query=form.data)

    data = controllers.sv_variants(store, variants_query, page)
    return dict(institute=institute_obj, case=case_obj, variant_type=variant_type,
                form=form, severe_so_terms=SEVERE_SO_TERMS, page=page, **data)

@variants_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variants/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = controllers.sv_variant(store, institute_id, case_name, variant_id)
    return data


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/priority',
                   methods=['POST'])
def manual_rank(institute_id, case_name, variant_id):
    """Update the manual variant rank for a variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    new_manual_rank = int(request.form['manual_rank'])
    link = request.referrer
    store.update_manual_rank(institute_obj, case_obj, user_obj, link, variant_obj,
                             new_manual_rank)
    return redirect(request.referrer)


@variants_bp.route('/<institute_id>/<case_name>/<variant_id>/sanger', methods=['POST'])
def sanger(institute_id, case_name, variant_id):
    """Send Sanger email for confirming a variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    user_obj = store.user(current_user.email)
    try:
        controllers.sanger(store, mail, institute_obj, case_obj, user_obj,
                           variant_obj, current_app.config['MAIL_USERNAME'])
    except controllers.MissingSangerRecipientError:
        flash('No sanger recipients added to institute.', 'danger')
    return redirect(request.referrer)
