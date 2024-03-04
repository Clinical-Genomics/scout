from typing import Optional, Tuple

from bson import json_util
from flask import Blueprint, Response, abort, url_for
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import institute_and_case, variant_institute_and_case

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")


@api_bp.route("/<institute_id>/<case_name>")
def case(institute_id, case_name):
    """Return a variant."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    if case_obj is None:
        return abort(404)
    return Response(json_util.dumps(case_obj), mimetype="application/json")


def _lookup_variant(
    variant_id: str,
    institute_id: Optional[str] = None,
    case_name: Optional[str] = None,
) -> Optional[Tuple[dict, dict, dict]]:
    """Lookup variant using variant document id. Return institute, case, and variant obj dicts.

    The institute and case lookup adds a bit of security, checking if user is admin or
    has access to institute and case, but since the variant is looked up using document_id,
    we also run an additional security check that the given case_id matches the variant case_id.

    The check without institute and case is strict, as the user cannot choose what institute to
    match against the ones the user has access to.
    """

    variant_obj = store.variant(variant_id)

    if not variant_obj:
        return abort(404)

    institute_obj, case_obj = variant_institute_and_case(
        store, variant_obj, institute_id, case_name
    )

    return (institute_obj, case_obj, variant_obj)


@api_bp.route("/<institute_id>/<case_name>/<variant_id>")
@api_bp.route("/variant/<variant_id>")
def variant(
    variant_id: str, institute_id: Optional[str] = None, case_name: Optional[str] = None
) -> Optional[Response]:
    """Display a specific SNV variant."""

    (_, _, variant_obj) = _lookup_variant(variant_id, institute_id, case_name)

    return Response(json_util.dumps(variant_obj), mimetype="application/json")


@api_bp.route("/<institute_id>/<case_name>/<variant_id>/pin")
@api_bp.route("/<variant_id>/pin")
def pin_variant(
    variant_id: str, institute_id: Optional[str] = None, case_name: Optional[str] = None
):
    """Pin an existing variant"""

    (institute_obj, case_obj, variant_obj) = _lookup_variant(variant_id, institute_id, case_name)

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
@api_bp.route("/<variant_id>/unpin")
def unpin_variant(
    variant_id: str, institute_id: Optional[str] = None, case_name: Optional[str] = None
):
    """Un-pin an existing, pinned variant"""

    (institute_obj, case_obj, variant_obj) = _lookup_variant(variant_id, institute_id, case_name)

    user_obj = store.user(current_user.email)
    link = url_for(
        "variant.variant",
        institute_id=institute_id,
        case_name=case_name,
        variant_id=variant_id,
    )
    store.unpin_variant(institute_obj, case_obj, user_obj, link, variant_obj)

    return Response(json_util.dumps(variant_obj), mimetype="application/json")
