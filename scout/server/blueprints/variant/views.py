from flask import Blueprint

from scout.server.utils import templated
from scout.server.extensions import store

from . import controllers

variant_bp = Blueprint('variant', __name__, static_folder='static', template_folder='templates')

@variant_bp.route('/<institute_id>/<case_name>/sv/variants/<variant_id>')
@templated('variants/sv-variant.html')
def sv_variant(institute_id, case_name, variant_id):
    """Display a specific structural variant."""
    data = controllers.sv_variant(store, institute_id, case_name, variant_id)
    return data
