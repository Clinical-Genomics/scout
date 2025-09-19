# -*- coding: utf-8 -*-
import logging
from typing import Optional

import requests
from flask import (
    Blueprint,
    Response,
    abort,
    render_template,
    request,
)
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import institute_and_case

from . import controllers
from .partial import send_file_partial

alignviewers_bp = Blueprint(
    "alignviewers",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/alignviewers/static",
)

LOG = logging.getLogger(__name__)


@alignviewers_bp.route("/remote/cors/<path:remote_url>", methods=["OPTIONS", "GET"])
def remote_cors(remote_url):
    """Proxy a remote URL.
    Useful to e.g. eliminate CORS issues when the remote site does not
        communicate CORS headers well, as in cloud tracks on figshare for IGV.js.

    Based on code from answers to this thread:
        https://stackoverflow.com/questions/6656363/proxying-to-another-web-service-with-flask/
    """
    # Check that user is logged in
    if current_user.is_authenticated is False:
        LOG.warning("Unauthenticated user requesting resource via remote_static")
        return abort(401)

    # And that the remote resource is among user tracks
    if controllers.authorize_config_custom_tracks(remote_url) is False:
        return abort(403)

    resp = requests.request(
        method=request.method,
        url=remote_url,
        headers={key: value for (key, value) in request.headers if key != "Host"},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=True,
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    response = Response(resp.content, resp.status_code, headers)
    return response


@alignviewers_bp.route("/remote/static", methods=["OPTIONS", "GET"])
def remote_static():
    """Stream *large* static files with special requirements."""
    file_path = request.args.get("file", default=".", type=str)
    institute_id = request.args.get("institute_id", default=".", type=str)
    case_name = request.args.get("case_name", default=".", type=str)

    # Check that user is logged in
    if current_user.is_authenticated is False:
        LOG.warning("Unauthenticated user requesting resource via remote_static")
        return abort(401)

    # Ensure the user really has access to this case's tracks by
    # retrieving case (only allowed if user has access)
    _, case_obj = institute_and_case(store, institute_id, case_name)

    if controllers.authorize_case_tracks(file_path, case_obj) is False:
        return abort(403)

    range_header = request.headers.get("Range", None)
    if not range_header and (file_path.endswith(".bam") or file_path.endswith(".cram")):
        return abort(500)

    new_resp = send_file_partial(file_path)
    return new_resp


@alignviewers_bp.route(
    "/<institute_id>/<case_name>/igv-splice-junctions", methods=["GET"]
)  # from case page
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/igv-splice-junctions", methods=["GET"]
)
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/outliers/<omics_variant_id>/igv-splice-junctions", methods=["GET"]
)
def sashimi_igv(
    institute_id: str,
    case_name: str,
    variant_id: Optional[str] = None,
    omics_variant_id: Optional[str] = None,
):
    """Visualize splice junctions on igv.js sashimi-like viewer for one or more individuals of a case.
    wiki: https://github.com/igvteam/igv.js/wiki/Splice-Junctions
    """
    _, case_obj = institute_and_case(
        store, institute_id, case_name
    )  # This function takes care of checking if user is authorized to see resource

    display_obj = controllers.make_sashimi_tracks(case_obj, variant_id, omics_variant_id)

    response = Response(render_template("alignviewers/igv_sashimi_viewer.html", **display_obj))

    return response


@alignviewers_bp.route("/<institute_id>/<case_name>/igv", methods=["GET"])  # from case page
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/igv", methods=["GET"]
)  # from SNV and STR variant page
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/<chrom>/<start>/<stop>/igv", methods=["GET"]
)  # from SV variant page, where you have to pass breakpoints coordinates
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/<chrom>/<start>/<stop>/igv", methods=["GET"]
)  # from SMN variant page
def igv(
    institute_id: str,
    case_name: str,
    variant_id: Optional[str] = None,
    chrom: Optional[str] = None,
    start: Optional[int] = None,
    stop: Optional[int] = None,
) -> Response:
    """Visualize BAM alignments using igv.js (https://github.com/igvteam/igv.js)."""
    _, case_obj = institute_and_case(
        store, institute_id, case_name
    )  # This function takes care of checking if user is authorized to see resource

    display_obj = controllers.make_igv_tracks(case_obj, variant_id, chrom, start, stop)

    response = Response(render_template("alignviewers/igv_viewer.html", **display_obj))
    return response
