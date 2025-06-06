"""Common utilities for the server code"""

import datetime
import logging
import os
import pathlib
import zipfile
from functools import wraps
from io import BytesIO
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import pdfkit
from bson.objectid import ObjectId
from flask import (
    Response,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
)
from flask_login import current_user
from werkzeug.local import LocalProxy

LOG = logging.getLogger(__name__)


def document_generated(document_id):
    """Returns the generation time of a certain MongodDB document

    Args:
        document_id (bson.objectid.ObjectId)

    Returns:
        document_id.generation_time (datetime.datetime) or None if document_id is not of type ObjectId
    """
    if isinstance(document_id, ObjectId):
        return document_id.generation_time
    LOG.error(f"Could not retrieve generation date for Object {document_id}")


def html_to_pdf_file(
    html_string, orientation, dpi=96, margins=["1.5cm", "1cm", "1cm", "1cm"], zoom=1
):
    """Creates a pdf file from the content of an HTML file
    Args:
        html_string(string): an HTML string to be rendered as PDF
        orientation(string): landscape, portrait
        dpi(int): dot density of the page to be printed
        margins(list): [ margin-top, margin-right, margin-bottom, margin-left], in cm
        zoom(float): change the size of the content on the pages

    Returns:
        bytes_file(BytesIO): a BytesIO file
    """
    options = {
        "page-size": "A4",
        "zoom": zoom,
        "orientation": orientation,
        "encoding": "UTF-8",
        "dpi": dpi,
        "margin-top": margins[0],
        "margin-right": margins[1],
        "margin-bottom": margins[2],
        "margin-left": margins[3],
        "enable-local-file-access": None,
    }
    pdf = pdfkit.from_string(html_string, False, options=options, verbose=True)
    bytes_file = BytesIO(pdf)
    return bytes_file


def jsonconverter(obj):
    """Converts non-serializable onjects into str"""
    LOG.warning(f"An object of type {type(obj)} is not json-serializable: converting it.")
    if "Form" in str(type(obj)):
        return obj.__dict__
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return obj.__str__()


def templated(template=None):
    """Template decorator.
    Ref: http://flask.pocoo.org/docs/patterns/viewdecorators/
    """

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint.replace(".", "/") + ".html"
            context = func(*args, **kwargs)
            if context is None:
                context = {}
            elif not isinstance(context, dict):
                return context
            return render_template(template_name, **context)

        return decorated_function

    return decorator


def public_endpoint(function):
    """Renders public endpoint"""
    function.is_public = True
    return function


def safe_redirect_back(request: LocalProxy, link: Optional[str] = None) -> Response:
    """Safely redirects the user back to the referring URL, if it originates from the same host.
    Otherwise, the user is redirected to a default '/'."""
    referrer = request.referrer
    if referrer:
        parsed_referrer = urlparse(referrer)
        if parsed_referrer.netloc == request.host:
            return redirect(link or referrer)
    return redirect("/")


def variant_institute_and_case(
    store, variant_obj: dict, institute_id: Optional[str], case_name: Optional[str]
) -> Tuple[dict, dict]:
    """Fetch insitiute and case objects.

    Ensure that case_id on the variant matches that of any case given.
    Ensure user has access to variant institute, or to the case through institute case sharing.
    """

    if not case_name:
        variant_case_obj = store.case(
            case_id=variant_obj["case_id"], projection={"display_name": 1}
        )
        case_name = variant_case_obj["display_name"]

    if not institute_id:
        institute_id = variant_obj["institute"]

    (institute_obj, case_obj) = institute_and_case(store, institute_id, case_name)

    if case_obj is None:
        return abort(404)

    if variant_obj.get("case_id") != case_obj.get("_id"):
        return abort(403)

    return (institute_obj, case_obj)


def institute_and_case(store, institute_id, case_name=None):
    """Fetch insitiute and case objects."""

    institute_obj = store.institute(institute_id)
    if institute_obj is None:
        flash("Can't find institute: {}".format(institute_id), "warning")
        return abort(404)

    if case_name:
        case_obj = store.case(institute_id=institute_id, display_name=case_name)
        if case_obj is None:
            return abort(404)

        # Make sure build is either "37" or "38"
        case_obj["genome_build"] = get_case_genome_build(case_obj)

    # validate that user has access to the institute

    if not current_user.is_admin:
        if institute_id not in current_user.institutes:
            if not case_name or not any(
                inst_id in case_obj["collaborators"] for inst_id in current_user.institutes
            ):
                # you don't have access!!
                flash("You don't have acccess to: {}".format(institute_id), "danger")
                return abort(403)

    # you have access!
    if case_name:
        return institute_obj, case_obj
    return institute_obj


def user_cases(store, login_user):
    """Returns all institutes with case count for a logged user

    Args:
        store(scout.adapter.mongo.base.MongoAdapter)
        login_user(werkzeug.local.LocalProxy)

    Returns:
        pymongo.Cursor
    """

    match_query = {
        "$match": {
            "collaborators": {"$in": login_user.institutes},
        }
    }  # Return only cases available for the user
    group = {
        "$group": {
            "_id": {
                "institute": "$owner",
            },
            "count": {"$sum": 1},
        }
    }  # Group cases by institute
    sort = {"$sort": {"_id.institute": 1}}  # Sort by inst _id ascending
    if login_user.is_admin:
        pipeline = [group, sort]
    else:
        pipeline = [match_query, group, sort]
    return store.case_collection.aggregate(pipeline)


def user_institutes(store, login_user):
    """Preprocess institute objects."""
    if login_user.is_admin:
        institutes = store.institutes()
    else:
        institutes = [store.institute(inst_id) for inst_id in login_user.institutes]

    return institutes


def get_case_genome_build(case_obj: dict) -> str:
    """returns the genome build of a case, as a string."""
    return "38" if "38" in str(case_obj.get("genome_build", "37")) else "37"


def get_case_mito_chromosome(case_obj: dict) -> str:
    """Returns MT or M, according to the genome build of a case."""
    case_build = get_case_genome_build(case_obj)
    if case_build == "38":
        return "M"
    return "MT"


def case_has_mtdna_report(case_obj: dict):
    """Display mtDNA report on the case sidebar only for some specific cases."""
    if case_obj.get("track", "rare") == "cancer":
        return
    for ind in case_obj.get("individuals", []):
        if ind.get("analysis_type") == "wts":
            continue
        case_obj["mtdna_report"] = True
        return


def case_has_chanjo_coverage(case_obj: dict):
    """Set case_obj["chanjo_coverage"] to True if there is an instance of chanjo available and case has coverage stats in chanjo."""

    chanjo_instance: bool = bool(current_app.config.get("chanjo_report"))
    if case_obj.get("track", "rare") != "cancer" and chanjo_instance:
        for ind in case_obj.get("individuals", []):
            if ind.get("analysis_type") != "wts":
                case_obj["chanjo_coverage"] = True
                return


def case_has_chanjo2_coverage(case_obj: dict):
    """Set case_obj["chanjo_coverage"] to True if if there is an instance of chanjo available and case has coverage stats in chanjo2."""

    chanjo2_instance: bool = bool(current_app.config.get("CHANJO2_URL"))
    if chanjo2_instance is False:
        return
    for ind in case_obj.get("individuals", []):
        ind_d4: str = ind.get("d4_file")
        if ind_d4 and os.path.exists(ind_d4):
            case_obj["chanjo2_coverage"] = True
            return


def case_has_alignments(case_obj: dict):
    """Add info on bam/cram files availability to a case dictionary

    This sets the availability of alignments for autosomal chromosomes.
    If paraphase or de novo assembly alignments, this is also sufficient to set
    alignment availability.
    Args:
        case_obj(scout.models.Case)
    """
    case_obj["bam_files"] = False
    for ind in case_obj.get("individuals"):
        for alignment_path_key in [
            "bam_file",
            "assembly_alignment_path",
            "paraphase_alignment_path",
        ]:
            bam_path = ind.get(alignment_path_key)
            if bam_path and os.path.exists(bam_path):
                case_obj["bam_files"] = True
                return


def case_has_mt_alignments(case_obj: dict):
    """Add info on MT bam files availability to a case dictionary

    Args:
        case_obj(scout.models.Case)
    """
    case_obj["mt_bams"] = False  # Availability of alignments for MT chromosome
    for ind in case_obj.get("individuals"):
        if _check_path_name(ind, "mt_bam"):
            case_obj["mt_bams"] = True
            return


def case_has_rna_tracks(case_obj: Dict) -> bool:
    """Returns True if one or more individuals of the case contain RNA-seq data
    Add this info to the case obj dict.

    Args:
        case_obj(dict)
    Returns
        True or False (bool)
    """
    # Display junctions track if available for any of the individuals
    case_obj["has_rna_tracks"] = False
    for ind in case_obj.get("individuals", []):
        # RNA can have three different aln track files
        for path_name in ["splice_junctions_bed", "rna_coverage_bigwig", "rna_alignment_path"]:
            if _check_path_name(ind, path_name):
                case_obj["has_rna_tracks"] = True
                return True
    return False


def _check_path_name(ind: Dict, path_name: str) -> bool:
    """Returns True if path with name path_name is set on individual and exists on disk."""

    path = ind.get(path_name)
    if path and os.path.exists(path):
        return True
    return False


def case_append_alignments(case_obj: dict):
    """Deconvolute information about files to case_obj.

    This function prepares bam/cram files and their indexes for easy access in templates.

    index is set only if it is expected as a separate key on the indiviudal: an
    attempt at discovery is still made for files with index: None.
    """
    unwrap_settings = [
        {"path": "bam_file", "append_to": "bam_files", "index": "bai_files"},
        {"path": "assembly_alignment_path", "append_to": "assembly_alignments", "index": None},
        {"path": "mt_bam", "append_to": "mt_bams", "index": "mt_bais"},
        {
            "path": "paraphase_alignment_path",
            "append_to": "paraphase_alignments",
            "index": None,
        },
        {"path": "rhocall_bed", "append_to": "rhocall_beds", "index": None},
        {"path": "rhocall_wig", "append_to": "rhocall_wigs", "index": None},
        {"path": "upd_regions_bed", "append_to": "upd_regions_beds", "index": None},
        {"path": "upd_sites_bed", "append_to": "upd_sites_beds", "index": None},
        {
            "path": "minor_allele_frequency_wig",
            "append_to": "minor_allele_frequency_wigs",
            "index": None,
        },
        {"path": "tiddit_coverage_wig", "append_to": "tiddit_coverage_wigs", "index": None},
    ]

    def process_file(case_obj, individual, setting):
        """Process a single file and its optional index."""
        file_path = individual.get(setting["path"])
        append_safe(
            case_obj,
            setting["append_to"],
            file_path if file_path and os.path.exists(file_path) else "missing",
        )
        if setting["index"]:
            index_path = (
                find_index(file_path) if file_path and os.path.exists(file_path) else "missing"
            )
            append_safe(case_obj, setting["index"], index_path)

    for individual in case_obj["individuals"]:
        # Add sample name
        sample_name = f"{case_obj.get('display_name', '')} - {individual.get('display_name', '')}"
        append_safe(case_obj, "sample_names", sample_name)
        append_safe(
            case_obj,
            "track_items_soft_clips_settings",
            individual.get("analysis_type", "") not in ["wes", "panel"],
        )

        # Process all file settings
        for setting in unwrap_settings:
            process_file(case_obj, individual, setting)


def append_safe(obj, obj_index, elem):
    """Append `elem` to list in `obj` at `obj_index`.
    If no list exists `elem` will be first element catching
    the KeyError raised."""
    try:
        obj[obj_index].append(elem)
    except KeyError:
        obj[obj_index] = [elem]


def find_index(align_file):
    """Find out BAI file by extension given the BAM file.

    Index files wither ends with filename.bam.bai or filename.bai /
    In case of cram alignments the index is named filename.cram.crai or filename.crai

    Args:
        align_file(str): The path to a bam/cram file

    Returns:
        index_file(str): Path to index file
    """
    index_file = None
    if align_file.endswith("cram"):
        index_file = align_file.replace(".cram", ".crai")
        if not os.path.exists(index_file):
            index_file = "{}.crai".format(align_file)
    else:
        index_file = align_file.replace(".bam", ".bai")
        if not os.path.exists(index_file):
            index_file = "{}.bai".format(align_file)
    return index_file


def zip_dir_to_obj(path):
    """
    Zip the temp files in a directory on the fly and serve the archive to the user

    Args:
        path: path

    Returns:
        data(io.BytesIO): zipped data object
    """

    data = BytesIO()
    with zipfile.ZipFile(data, mode="w") as z:
        for f_name in pathlib.Path(path).iterdir():
            z.write(f_name, os.path.basename(f_name))
    data.seek(0)

    return data
