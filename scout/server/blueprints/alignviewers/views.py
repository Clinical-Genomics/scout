# -*- coding: utf-8 -*-
import logging
import os.path

from flask import (
    abort,
    Blueprint,
    render_template,
    send_file,
    request,
    current_app,
    flash,
)

from .partial import send_file_partial
from scout.constants import HUMAN_REFERENCE
from . import controllers

alignviewers_bp = Blueprint(
    "alignviewers",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/alignviewers/static",
)

LOG = logging.getLogger(__name__)


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

    # Set up IGV tracks that are common for all cases:
    display_obj["reference_track"] = HUMAN_REFERENCE[
        chromosome_build
    ]  # Human reference is always present
    # General tracks (Genes, Clinvar and ClinVar SNVs are shown according to user preferences)
    controllers.set_common_tracks(display_obj, chromosome_build, request.form)

    # Set up bam/cram alignments for case samples:
    controllers.set_sample_tracks(display_obj, request.form)

    # When chrom != MT, set up case-specific tracks (might be present according to the pipeline)
    if chrom != "M":
        controllers.set_case_specific_tracks(display_obj, request.form)

    display_obj["display_center_guide"] = True

    return render_template("alignviewers/igv_viewer.html", locus=locus, **display_obj)
