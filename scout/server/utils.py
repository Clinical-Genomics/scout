"""Common utilities for the server code"""
import datetime
import io
import logging
import os
import pathlib
import zipfile
from functools import wraps

from bson.objectid import ObjectId
from flask import abort, flash, render_template, request
from flask_login import current_user

LOG = logging.getLogger(__name__)


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


def user_institutes(store, login_user):
    """Preprocess institute objects."""
    if login_user.is_admin:
        institutes = store.institutes()
    else:
        institutes = [store.institute(inst_id) for inst_id in login_user.institutes]

    return institutes


def variant_case(store, case_obj, variant_obj):
    """Pre-process case for the variant view.

    Adds information about files from case obj to variant

    Args:
        store(scout.adapter.MongoAdapter)
        case_obj(scout.models.Case)
        variant_obj(scout.models.Variant)
    """

    case_append_alignments(case_obj)

    chrom = None
    starts = []
    ends = []
    for gene in variant_obj.get("genes", []):
        common_info = gene.get("common")
        if not common_info:
            continue
        chrom = common_info.get("chromosome")
        starts.append(common_info.get("start"))
        ends.append(common_info.get("end"))

    if not (chrom and starts and ends):
        return

    try:
        vcf_path = store.get_region_vcf(case_obj, chrom=chrom, start=min(starts), end=max(ends))

        # Create a reduced VCF with variants in the region
        case_obj["region_vcf_file"] = vcf_path
    except FileNotFoundError as err:
        LOG.warning(err)


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
            case_obj["display_name"] + " - " + individual.get("display_name"),
        )
        for setting in unwrap_settings:
            file_path = individual.get(setting["path"])
            LOG.debug("filepath %s: ", file_path)
            if not (file_path and os.path.exists(file_path)):
                LOG.debug("%s: no bam/cram file found", individual["individual_id"])
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

    data = io.BytesIO()
    with zipfile.ZipFile(data, mode="w") as z:
        for f_name in pathlib.Path(path).iterdir():
            z.write(f_name, os.path.basename(f_name))
    data.seek(0)

    return data
