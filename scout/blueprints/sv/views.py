# -*- coding: utf-8 -*-
from flask import abort, Blueprint, request
from flask_login import login_required, current_user

from scout.extensions import store
from scout.utils.helpers import templated, validate_user

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

    per_page = 50
    skip = int(request.args.get('skip', 0))
    current_batch = skip + per_page

    # fetch list of variants
    query = {'variant_type': request.args.get('variant_type', 'clinical')}
    all_variants, count = store.variants(case_model.case_id,
                                         category='sv',
                                         query=query,
                                         nr_of_variants=per_page,
                                         skip=skip)
    return dict(case=case_model,
                case_id=case_id,
                institute=institute,
                institute_id=institute_id,
                variants=all_variants,
                variants_count=count,
                current_batch=current_batch,
                query=query,
                per_page=per_page, skip=skip)


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

    overlapping_snvs = store.overlapping(variant_model)
    return dict(institute=institute, institute_id=institute_id,
                case=case_model, case_id=case_id,
                variant=variant_model, variant_id=variant_id,
                overlapping_snvs=overlapping_snvs)
