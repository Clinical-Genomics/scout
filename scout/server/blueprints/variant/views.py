import logging
from datetime import datetime

from flask import (Blueprint, flash, current_app, redirect, request)

from scout.server.utils import templated
from scout.server.extensions import (store, loqusdb)

from . import controllers

LOG = logging.getLogger(__name__)

variant_bp = Blueprint('variant', __name__, static_folder='static', template_folder='templates')

@variant_bp.route('/<institute_id>/<case_name>/<variant_id>')
@templated('variant/variant.html')
def variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    LOG.debug("Variants view requesting data for variant {}".format(variant_id))
    start_time = datetime.now()
    data = controllers.variant(store, institute_id, case_name, variant_id=variant_id, 
                               variant_type='snv')
    if data is None:
        LOG.warning("An error occurred: variants view requesting data for variant {}".format(variant_id))
        flash('An error occurred while retrieving variant object', 'danger')
        return redirect(request.referrer)

    if current_app.config.get('LOQUSDB_SETTINGS'):
        data['observations'] = controllers.observations(store, loqusdb,
            case_obj, data['variant'])
    data['cancer'] = request.args.get('cancer') == 'yes'
    return data

@variant_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variant/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = controllers.variant(store, institute_id, case_name, variant_id, add_other=False, 
                               variant_type='sv')
    return data

@variant_bp.route('/<institute_id>/<case_name>/str/variants/<variant_id>')
@templated('variant/str-variant.html')
def str_variant(institute_id, case_name, variant_id):
    """Display a specific STR variant."""
    data = controllers.variant(store, institute_id, case_name, variant_id, add_other=False, 
                               get_overlapping=False, variant_type='str')
    return data
