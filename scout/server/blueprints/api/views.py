from bson import json_util
from flask import Blueprint, Response, abort, url_for
from flask_login import current_user

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
    variant_obj = store.variant(variant_id)
    return Response(json_util.dumps(variant_obj), mimetype="application/json")


@api_bp.route("/<institute_id>/<case_name>/<variant_id>/pin")
@api_bp.route("/<variant_id>/pin")
def pin_variant(variant_id, institute_id=None, case_name=None):
    """Pin an existing variant

    We always want to check institute_and_case with the case name and institute given on the variant object,
    not only the one give on the URL, to ensure user permissions are ok.
    """
    variant_obj = store.variant(variant_id)

    variant_case_obj = store.case(case_id=variant_obj["case_id"])
    variant_case_name = variant_case_obj["display_name"]

    variant_institute_id = variant_obj["institute"]

    institute_obj, case_obj = institute_and_case(store, variant_institute_id, variant_case_name)

    if institute_id and case_name:
        institute_obj, case_obj = institute_and_case(store, institute_id, case_name)

    user_obj = store.user(current_user.email)
    link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    store.pin_variant(institute_obj, case_obj, user_obj, link, variant_obj)

    return Response(json_util.dumps(variant_obj), mimetype="application/json")


@api_bp.route("/<institute_id>/<case_name>/<variant_id>/unpin")
def unpin_variant(institute_id, case_name, variant_id):
    """Un-pin an existing, pinned variant"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    variant_obj = store.variant(variant_id)

    user_obj = store.user(current_user.email)
    link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    store.unpin_variant(institute_obj, case_obj, user_obj, link, variant_obj)

    return Response(json_util.dumps(variant_obj), mimetype="application/json")
