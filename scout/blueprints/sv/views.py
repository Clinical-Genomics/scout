# -*- coding: utf-8 -*-
from flask import (abort, Blueprint, current_app, request, make_response)
from flask_login import login_required, current_user

from scout.models import Variant
from scout.extensions import store, loqusdb
from scout.utils import templated, validate_user

sv_bp = Blueprint('sv', __name__, template_folder='templates',
                  static_folder='static', static_url_path='/sv/static')


@sv_bp.route('/<institute_id>/<case_id>/sv/variants')
@templated('sv/variants.html')
@login_required
def variants(institute_id, case_id):
    """View all variants for a single case."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    if case_model is None:
        abort(404)

    # fetch list of variants
    variant_models = store.variants(case_id, category='sv')
    return dict(variants=variant_models,
                case=case_model,
                case_id=case_id,
                institute=institute,
                institute_id=institute_id)


@sv_bp.route('/<institute_id>/<case_id>/sv/variants/<variant_id>')
@templated('sv/variant.html')
@login_required
def variant(institute_id, case_id, variant_id):
    """View a single variant in a single case."""
    institute = validate_user(current_user, institute_id)
    case_model = store.case(institute_id, case_id)
    variant_model = store.variant(document_id=variant_id)
    if variant_model is None:
        return abort(404, 'variant not found')

    comments = store.events(institute, case=case_model,
                            variant_id=variant_model.variant_id,
                            comments=True)
    events = store.events(institute, case=case_model,
                          variant_id=variant_model.variant_id)

    individuals = {individual.individual_id: individual
                   for individual in case_model.individuals}

    # coverage link for gene
    coverage_links = genecov_links(case_model.individuals,
                                   variant_model.hgnc_symbols)

    prev_variant = store.previous_variant(document_id=variant_id)
    next_variant = store.next_variant(document_id=variant_id)

    local_freq = loqusdb.get_variant({'_id': variant_model.composite_id})
    local_total = loqusdb.case_count()

    causatives = store.other_causatives(case_model, variant_model)

    return dict(institute=institute, institute_id=institute_id,
                case=case_model, case_id=case_id,
                variant=variant_model, variant_id=variant_id,
                comments=comments, events=events,
                prev_variant=prev_variant, next_variant=next_variant,
                manual_rank_options=Variant.manual_rank.choices,
                individuals=individuals, coverage_links=coverage_links,
                local_freq=local_freq, local_total=local_total,
                causatives=causatives)
