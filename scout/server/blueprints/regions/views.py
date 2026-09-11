import logging

from flask import Blueprint, jsonify, request
from pymongo.errors import OperationFailure

from scout.server.blueprints.regions.controllers import isca_region as region_controller
from scout.server.blueprints.regions.controllers import regions as regions_controller
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


@regions_bp.route("/api/v1/regions", methods=["GET"])
@public_endpoint
def api_regions():
    """Return JSON data about regions."""
    query = request.values.get("query")

    build = get_build(request)

    json_out = {"regions": store.get_regions(build, query)}
    return jsonify(json_out)


@regions_bp.route("/api/v1/regionlist", methods=["GET"])
def api_regionlist():
    """Return JSON data about the list of regions."""
    build = get_build(request)
    query = request.values.get("query")

    try:
        regions = store.get_regions(build=build, query=query)
    except OperationFailure as of:
        return jsonify({"error": of._message})

    json_terms = [
        {"name": f"{region['isca_id']} | {region['display_name']}", "id": region["isca_id"]}
        for region in regions
    ]
    return jsonify(json_terms)


@regions_bp.route("/regions", methods=["GET"])
@templated("regions/regions.html")
def regions():
    """Render information about regions."""
    return regions_controller(store)


@regions_bp.route("/isca_region/<isca_id>", methods=["GET"])
@templated("regions/isca_region.html")
def isca_region(isca_id):
    """Render information about a region."""
    build = get_build(request)
    return region_controller(store, f"{isca_id}", build)
