"""Common utilities for the server code"""
import datetime
import logging
import os
import pathlib
import zipfile
from functools import wraps
from io import BytesIO
from typing import Dict, Optional, Tuple

import pdfkit
from bson.objectid import ObjectId
from flask import abort, flash, render_template, request
from flask_login import current_user

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
        case_obj["genome_build"] = "38" if "38" in str(case_obj.get("genome_build")) else "37"

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


def case_has_alignments(case_obj):
    """Add info on bam/cram files availability to a case dictionary

    Args:
        case_obj(scout.models.Case)
    """
    case_obj["bam_files"] = False  # Availability of alignments for autosomal chromosomes
    for ind in case_obj.get("individuals"):
        bam_path = ind.get("bam_file")
        if bam_path and os.path.exists(bam_path):
            case_obj["bam_files"] = True
            return


def case_has_mt_alignments(case_obj: Dict):
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
    """Returns True if one of more individuals of the case contain RNA-seq data

    Args:
        case_obj(dict)
    Returns
        True or False (bool)
    """
    # Display junctions track if available for any of the individuals
    for ind in case_obj.get("individuals", []):
        # RNA can have three different aln track files
        for path_name in ["splice_junctions_bed", "rna_coverage_bigwig", "rna_alignment_path"]:
            if _check_path_name(ind, path_name):
                return True
    return False


def _check_path_name(ind: Dict, path_name: str) -> bool:
    """Returns True if path with name path_name is set on individual and exists on disk."""

    path = ind.get(path_name)
    if path and os.path.exists(path):
        return True
    return False


def case_append_alignments(case_obj):
    """Deconvolute information about files to case_obj.

    This function prepares the bam/cram files in a certain way so that they are easily accessed in
    the templates.

    Loops over the the individuals and gather bam/cram files, indexes and sample display names in
    lists

    Args:
        case_obj(scout.models.Case)
    """
    unwrap_settings = [
        {"path": "bam_file", "append_to": "bam_files", "index": "bai_files"},
        {"path": "mt_bam", "append_to": "mt_bams", "index": "mt_bais"},
        {"path": "rhocall_bed", "append_to": "rhocall_beds", "index": "no_index"},
        {"path": "rhocall_wig", "append_to": "rhocall_wigs", "index": "no_index"},
        {
            "path": "upd_regions_bed",
            "append_to": "upd_regions_beds",
            "index": "no_index",
        },
        {"path": "upd_sites_bed", "append_to": "upd_sites_beds", "index": "no_index"},
        {
            "path": "tiddit_coverage_wig",
            "append_to": "tiddit_coverage_wigs",
            "index": "no_index",
        },
    ]

    for individual in case_obj["individuals"]:
        append_safe(
            case_obj,
            "sample_names",
            case_obj.get("display_name", "") + " - " + individual.get("display_name", ""),
        )
        for setting in unwrap_settings:
            file_path = individual.get(setting["path"])
            if not (file_path and os.path.exists(file_path)):
                continue
            append_safe(case_obj, setting["append_to"], file_path)
            if not setting["index"] == "no_index":
                append_safe(
                    case_obj, setting["index"], find_index(file_path)
                )  # either bai_files or mt_bais


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
