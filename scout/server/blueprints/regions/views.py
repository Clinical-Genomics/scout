import logging

from flask import Blueprint, jsonify, request

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


@regions_bp.route("/api/v1/regions")
@public_endpoint
def api_regions():
    """Return JSON data about regions."""
    query = request.values.get("query")

    build = get_build(request)

    json_out = {"regions": store.get_regions(build, query)}
    return jsonify(json_out)


@regions_bp.route("/regions")
@templated("regions/regions.html")
def regions():
    """Render information about regions."""
    return regions_controller(store)


@regions_bp.route("/isca_region/<isca_id>")
@templated("regions/isca_region.html")
def isca_region(isca_id):
    """Render information about a region."""
    build = get_build(request)
    return region_controller(store, f"{isca_id}", build)
