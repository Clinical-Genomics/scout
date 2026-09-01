import logging

from flask import Blueprint, jsonify, request

from scout.server.blueprints.regions.controllers import region as region_controller
from scout.server.blueprints.regions.controllers import regions as regions_controller
from scout.server.blueprints.regions.controllers import regions_to_bed
from scout.server.extensions import store
from scout.server.utils import public_endpoint, templated

LOG = logging.getLogger(__name__)

regions_bp = Blueprint(
    "regions",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/regions/static",
)


def get_build(request):
    """Get build from request values, default to 38 if not specified"""
    request_build = request.values.get("build") or "38"
    build = "37" if "37" in request_build else "38"
    return build


@regions_bp.route("/api/v1/regions")
@public_endpoint
def api_regions():
    """Return JSON data about regions."""
    query = request.values.get("query")
    if query is None or query.replace("-", "").isalnum() is False:
        return jsonify({"code": 400, "message": "missing or invalid 'query' param in request"})

    build = get_build(request)

    json_out = {"regions": store.get_regions(build, query)}
    return jsonify(json_out)


@regions_bp.route("/api/v1/regions/bed")
@public_endpoint
def api_regions_bed():
    """Return bed data about regions."""
    query = request.values.get("query")
    if query is None or query.replace("-", "").isalnum() is False:
        return jsonify({"code": 400, "message": "missing or invalid 'query' param in request"})

    build = get_build(request)
    json_out = regions_to_bed(store, query, build)
    return jsonify(json_out)


@regions_bp.route("/regions")
@templated("regions/regions.html")
def regions():
    """Render information about regions."""
    build = get_build(request)
    data = {
        "build": build,
        "counts": store.region_type_count(),
    }
    return data


@regions_bp.route("/region/<isca_id>")
@templated("regions/region.html")
def region(isca_id):
    """Render information about a region."""
    build = get_build(request)
    data = {
        "build": build,
        "region": region_controller(store, {"isca_id": f"{isca_id}"}, build),
    }
    return data
