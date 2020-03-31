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
    chrom = request.form.get("contig")
    if chrom == "MT":
        chrom = "M"

    start = request.form.get("start")
    stop = request.form.get("stop")

    locus = "chr{0}:{1}-{2}".format(chrom, start, stop)
    LOG.debug("Displaying locus %s", locus)

    chromosome_build = request.form.get("build")
    LOG.debug("Chromosome build is %s", chromosome_build)

    samples = request.form.get("sample").split(",")
    LOG.debug("samples: %s", samples)

    bam_files = None
    bai_files = None
    rhocall_bed_files = None
    rhocall_wig_files = None
    tiddit_coverage_files = None
    updregion_files = None
    updsites_files = None

    if request.form.get("align") == "mt_bam":
        bam_files = request.form.get("mt_bam").split(",")
        bai_files = request.form.get("mt_bai").split(",")
    else:
        if request.form.get("bam"):
            bam_files = request.form.get("bam").split(",")
            LOG.debug("loading the following BAM tracks: %s", bam_files)
        if request.form.get("bai"):
            bai_files = request.form.get("bai").split(",")
        if request.form.get("rhocall_bed"):
            rhocall_bed_files = request.form.get("rhocall_bed").split(",")
            LOG.debug("loading the following rhocall BED tracks: %s", rhocall_bed_files)
        if request.form.get("rhocall_wig"):
            rhocall_wig_files = request.form.get("rhocall_wig").split(",")
            LOG.debug("loading the following rhocall WIG tracks: %s", rhocall_wig_files)
        if request.form.get("tiddit_coverage_wig"):
            tiddit_coverage_files = request.form.get("tiddit_coverage_wig").split(",")
            LOG.debug(
                "loading the following tiddit_coverage tracks: %s",
                tiddit_coverage_files,
            )
        if request.form.get("upd_regions_bed"):
            updregion_files = request.form.get("upd_regions_bed").split(",")
            LOG.debug("loading the following upd sites tracks: %s", updregion_files)
        if request.form.get("upd_sites_bed"):
            updsites_files = request.form.get("upd_sites_bed").split(",")
            LOG.debug("loading the following upd region tracks: %s", updsites_files)

    display_obj = {}

    display_obj["reference_track"] = controllers.reference_track(
        chromosome_build, chrom
    )
    display_obj["genes_track"] = controllers.genes_track(chromosome_build, chrom)
    display_obj["clinvar_snvs"] = controllers.clinvar_track(chromosome_build, chrom)
    display_obj["clinvar_cnvs"] = controllers.clinvar_cnvs_track(
        chromosome_build, chrom
    )

    # Init upcoming igv-tracks
    sample_tracks = []
    upd_regions_bed_tracks = []
    upd_sites_bed_tracks = []

    counter = 0
    for sample in samples:
        # some samples might not have an associated bam file, take care if this
        if len(bam_files) > counter and bam_files[counter]:
            sample_tracks.append(
                {
                    "name": sample,
                    "url": bam_files[counter],
                    "format": bam_files[counter].split(".")[-1],  # "bam" or "cram"
                    "indexURL": bai_files[counter],
                    "height": 700,
                }
            )
        counter += 1

    display_obj["sample_tracks"] = sample_tracks

    if rhocall_wig_files:
        rhocall_wig_tracks = make_igv_tracks("Rhocall Zygosity", rhocall_wig_files)
        display_obj["rhocall_wig_tracks"] = rhocall_wig_tracks
    if rhocall_bed_files:
        rhocall_bed_tracks = make_igv_tracks("Rhocall Regions", rhocall_bed_files)
        display_obj["rhocall_bed_tracks"] = rhocall_bed_tracks
    if tiddit_coverage_files:
        tiddit_wig_tracks = make_igv_tracks("TIDDIT Coverage", tiddit_coverage_files)
        display_obj["tiddit_wig_tracks"] = tiddit_wig_tracks
    if updregion_files:
        updregion_tracks = make_igv_tracks("UPD region", updregion_files)
        display_obj["updregion_tracks"] = updregion_tracks
    if updsites_files:
        updsites_tracks = make_igv_tracks("UPD sites", updsites_files)
        display_obj["updsites_tracks"] = updsites_tracks

    if request.form.get("center_guide"):
        display_obj["display_center_guide"] = True
    else:
        display_obj["display_center_guide"] = False

    return render_template("alignviewers/igv_viewer.html", locus=locus, **display_obj)


def make_igv_tracks(name, file_list):
    """ Return a dict according to IGV track format. """

    track_list = []
    counter = 0
    for r in file_list:
        track_list.append(
            {"name": name, "url": file_list[counter], "min": 0.0, "max": 30.0}
        )
        counter += 1
    return track_list
