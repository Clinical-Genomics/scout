# -*- coding: utf-8 -*-
import logging
import os.path

import requests
from flask import Blueprint, Response, abort, flash, redirect, render_template, request, send_file
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import institute_and_case, user_institutes

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
    LOG.debug("Got request: %s", request)

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
    file_path = request.args.get("file") or ""
    range_header = request.headers.get("Range", None)
    if not range_header and (file_path.endswith(".bam") or file_path.endswith(".cram")):
        return abort(500)

    new_resp = send_file_partial(file_path)
    return new_resp


@alignviewers_bp.route("/remote/static/unindexed", methods=["OPTIONS", "GET"])
def unindexed_remote_static():
    file_path = request.args.get("file")
    base_name = os.path.basename(file_path)
    resp = send_file(file_path, attachment_filename=base_name)
    return resp


@alignviewers_bp.route(
    "/igv-splice-junctions/<institute_id>/<case_name>/<variant_id>", methods=["GET"]
)
def sashimi_igv(institute_id, case_name, variant_id):
    """Visualize splice junctions on igv.js sashimi-like viewer for one or more individuals of a case.
    wiki: https://github.com/igvteam/igv.js/wiki/Splice-Junctions
    """
    _, case_obj = institute_and_case(store, institute_id, case_name)
    if (
        current_user.is_admin
        or institute_id in current_user.institutes
        or list(set(current_user.institutes) & set(case_obj.get("collaborators", [])))
    ):
        display_obj = controllers.make_sashimi_tracks(case_obj, variant_id)
        return render_template("alignviewers/igv_sashimi_viewer.html", **display_obj)
    else:
        flash(
            f"Current user doesn't have access to institute `{institute_id}`, case `{case_name}`",
            "warning",
        )
        return redirect(request.referrer)


@alignviewers_bp.route("/igv-viewer/<institute_id>/<case_name>", methods=["GET"])
def igv(institute_id, case_name, variant_id=None, chrom=None, start=None, stop=None):
    """Visualize BAM alignments using igv.js (https://github.com/igvteam/igv.js)

    Accepts:
        institute_id(str): _id of an institute
        case_name(str): dislay_name of a case
        variant_id(str/None): variant _id or None
        chrom(str/None): requested chromosome [1-22], X, Y, [M-MT]
        start(int/None): start of the genomic interval to be displayed
        stop(int/None): stop of the genomic interval to be displayed

    Returns:
        a string, corresponging to the HTML rendering of the IGV alignments page
    """
    _, case_obj = institute_and_case(store, institute_id, case_name)
    if (
        current_user.is_admin
        or institute_id in current_user.institutes
        or list(set(current_user.institutes) & set(case_obj.get("collaborators", [])))
    ):
        display_obj = controllers.make_igv_tracks(case_obj, variant_id, chrom, start, stop)
        return render_template("alignviewers/igv_viewer.html", **display_obj)
    else:
        flash(
            f"Current user doesn't have access to institute `{institute_id}`, case `{case_name}`",
            "warning",
        )
        return redirect(request.referrer)
