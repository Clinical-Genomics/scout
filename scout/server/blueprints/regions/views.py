import logging

from flask import Blueprint, jsonify, request

from scout.server.blueprints.regions.controllers import regions_to_bed, regions_to_json
from scout.server.extensions import store
from scout.server.utils import public_endpoint, templated

LOG = logging.getLogger(__name__)

regions_bp = Blueprint("regions", __name__, template_folder="templates")


@regions_bp.route("/api/v1/regions")
@public_endpoint
def api_regions():
    """Return JSON data about regions."""
    query = request.args.get("query")
    if query is None or query.replace("-", "").isalnum() is False:
        return jsonify({"code": 400, "message": "missing or invalid 'query' param in request"})
    build = request.args.get("build")

    json_out = regions_to_json(store, query, build)
    return jsonify(json_out)


@regions_bp.route("/api/v1/regions/bed")
@public_endpoint
def api_regions_bed():
    """Return bed data about regions."""
    query = request.args.get("query")
    if query is None or query.replace("-", "").isalnum() is False:
        return jsonify({"code": 400, "message": "missing or invalid 'query' param in request"})
    build = request.args.get("build")

    json_out = regions_to_bed(store, query, build)
    return jsonify(json_out)


@regions_bp.route("/regions/<query>")
@templated("regions/regions.html")
def regions(query):
    """Render information about regions."""
    build = request.args.get("build")
    data = {
        "query": query,
        "build": build,
        "regions": regions_to_json(store, query, build),
    }
    return data


@regions_bp.route("/region/<region_type>/<region_id>")
@templated("regions/region.html")
def region(region_type, region_id):
    """Render information about a region."""
