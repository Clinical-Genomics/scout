from bson import json_util
from flask import Blueprint, Response, abort

from scout.server.extensions import store
from scout.server.utils import institute_and_case

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/<institute_id>/<case_name>")
def case(institute_id, case_name):
    """Return a variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    if case_obj is None:
        return abort(404)
    return Response(json_util.dumps(case_obj), mimetype="application/json")


@api_bp.route("/<institute_id>/<case_name>/<variant_id>")
def variant(institute_id, case_name, variant_id):
    """Display a specific SNV variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)
    return Response(json_util.dumps(variant_obj), mimetype="application/json")
