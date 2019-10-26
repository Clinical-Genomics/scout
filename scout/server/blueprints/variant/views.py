import logging

from flask import (Blueprint, request, redirect, flash, current_app)

from scout.server.utils import templated
from scout.server.extensions import (store, loqusdb)
from scout.server.blueprints.variant.controllers import variant as variant_controller
from scout.server.blueprints.variant.controllers import observations


LOG = logging.getLogger(__name__)

variant_bp = Blueprint('variant', __name__, static_folder='static', template_folder='templates')

@variant_bp.route('/<institute_id>/<case_name>/<variant_id>')
@templated('variant/variant.html')
def variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    LOG.debug("Variants view requesting data for variant %s", variant_id)
    data = variant_controller(store, institute_id, case_name, variant_id=variant_id,
                               variant_type='snv')
    if data is None:
        LOG.warning("An error occurred: variants view requesting data for variant {}".format(variant_id))
        flash('An error occurred while retrieving variant object', 'danger')
        return redirect(request.referrer)

    if current_app.config.get('LOQUSDB_SETTINGS'):
        LOG.debug("Fetching loqusdb information for %s", variant_id)
        data['observations'] = observations(store, loqusdb, case_obj, data['variant'])
    
    data['cancer'] = request.args.get('cancer') == 'yes'
    data['str'] = request.args.get('str') == 'yes'
    return data

@variant_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variant/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = variant_controller(store, institute_id, case_name, variant_id, add_other=False, 
                               variant_type='sv')
    return data

@variant_bp.route('/<institute_id>/<case_name>/str/variants/<variant_id>')
@templated('variant/str-variant.html')
def str_variant(institute_id, case_name, variant_id):
    """Display a specific STR variant."""
    data = variant_controller(store, institute_id, case_name, variant_id, add_other=False,
                              get_overlapping=False, variant_type='str')
    return data
