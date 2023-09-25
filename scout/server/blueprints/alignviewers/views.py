# -*- coding: utf-8 -*-
import logging

import requests
from flask import (
    Blueprint,
    Response,
    abort,
    copy_current_request_context,
    render_template,
    request,
    session,
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
    # Check that user is logged in or that file extension is valid
    if controllers.check_session_tracks(remote_url) is False:
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
    file_path = request.args.get("file") or "."

    # Check that user is logged in or that file extension is valid
    if controllers.check_session_tracks(file_path) is False:
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
def sashimi_igv(institute_id, case_name, variant_id=None):
    """Visualize splice junctions on igv.js sashimi-like viewer for one or more individuals of a case.
    wiki: https://github.com/igvteam/igv.js/wiki/Splice-Junctions
    """
    _, case_obj = institute_and_case(
        store, institute_id, case_name
    )  # This function takes care of checking if user is authorized to see resource

    display_obj = controllers.make_sashimi_tracks(case_obj, variant_id)
    controllers.set_session_tracks(display_obj)

    response = Response(render_template("alignviewers/igv_sashimi_viewer.html", **display_obj))

    @response.call_on_close
    @copy_current_request_context
    def clear_session_tracks():
        session.pop("igv_tracks", None)  # clean up igv session tracks

    return response


@alignviewers_bp.route("/<institute_id>/<case_name>/igv", methods=["GET"])  # from case page
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/igv", methods=["GET"]
)  # from SNV and STR variant page
@alignviewers_bp.route(
    "/<institute_id>/<case_name>/<variant_id>/<chrom>/<start>/<stop>/igv", methods=["GET"]
)  # from SV variant page, where you have to pass breakpoints coordinates
def igv(institute_id, case_name, variant_id=None, chrom=None, start=None, stop=None):
    """Visualize BAM alignments using igv.js (https://github.com/igvteam/igv.js)

    Args:
        institute_id(str): _id of an institute
        case_name(str): dislay_name of a case
        variant_id(str/None): variant _id or None
        chrom(str/None): requested chromosome [1-22], X, Y, [M-MT]
        start(int/None): start of the genomic interval to be displayed
        stop(int/None): stop of the genomic interval to be displayed

    Returns:
        a string, corresponging to the HTML rendering of the IGV alignments page
    """
    _, case_obj = institute_and_case(
        store, institute_id, case_name
    )  # This function takes care of checking if user is authorized to see resource

    display_obj = controllers.make_igv_tracks(case_obj, variant_id, chrom, start, stop)
    controllers.set_session_tracks(display_obj)

    response = Response(render_template("alignviewers/igv_viewer.html", **display_obj))

    @response.call_on_close
    @copy_current_request_context
    def clear_session_tracks():
        session.pop("igv_tracks", None)  # clean up igv session tracks

    return response
