# -*- coding: utf-8 -*-
import logging
import os.path

import requests
from flask import (
    Blueprint,
    Response,
    abort,
    current_app,
    flash,
    render_template,
    request,
    send_file,
)

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

    excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
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
    file_path = request.args.get("file")
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
    display_obj = controllers.make_sashimi_tracks(institute_id, case_name, variant_id)
    return render_template("alignviewers/igv_sashimi_viewer.html", **display_obj)


@alignviewers_bp.route("/igv", methods=["POST"])
def igv():
    """Visualize BAM alignments using igv.js (https://github.com/igvteam/igv.js)"""

    # Set genome build for displaying alignments:
    # Genome build is 37 if request.form.get("build") is 37 and chr != MT
    # Genome build is 38 if request.form.get("build") is 38 or if chrom == MT
    chromosome_build = request.form.get("build")
    chrom = request.form.get("contig")
    if chrom == "MT":
        chrom = "M"
    if chromosome_build in ["GRCh38", "38"] or chrom == "M":
        chromosome_build = "38"
    else:
        chromosome_build = "37"

    start = request.form.get("start")
    stop = request.form.get("stop")
    locus = "chr{0}:{1}-{2}".format(chrom, start, stop)

    display_obj = {}  # Initialize the dictionary containing all tracks info

    # General tracks (Genes, Clinvar and ClinVar SNVs are shown according to user preferences)
    controllers.set_common_tracks(display_obj, chromosome_build)

    # Set up bam/cram alignments for case samples:
    controllers.set_sample_tracks(display_obj, request.form)

    # When chrom != MT, set up case-specific tracks (might be present according to the pipeline)
    if chrom != "M":
        controllers.set_case_specific_tracks(display_obj, request.form)

    # Set up custom cloud public tracks, if available
    controllers.set_cloud_public_tracks(display_obj, chromosome_build)

    display_obj["display_center_guide"] = True

    return render_template("alignviewers/igv_viewer.html", locus=locus, **display_obj)
