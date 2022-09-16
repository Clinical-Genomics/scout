import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for

from scout.constants.clinvar import CASEDATA_HEADER, CLINVAR_HEADER
from scout.server.extensions import store
from scout.server.utils import institute_and_case

from . import controllers

LOG = logging.getLogger(__name__)

blueprint = Blueprint("clinvar", __name__, template_folder="templates")


@blueprint.route("/<institute_id>/<case_name>/clinvar", methods=["POST"])
def clinvar_add_variant(institute_id, case_name):
    """Create a ClinVar submission document in database for one or more variants from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {"institute": institute_obj, "case": case_obj}
    controllers.set_clinvar_form(request.form.get("var_id"), data)
    return render_template("clinvar_add_one.html", **data)


@blueprint.route("/<institute_id>/<case_name>/clinvar_add_var", methods=["POST"])
def add_variant(institute_id, case_name):
    """Adds one variant with eventual CaseData observations to an open (or new) ClinVar submission"""

    variant_data = controllers.parse_variant_form_fields(request.form)  # dictionary
    casedata_list = controllers.parse_casedata_form_fields(request.form)  # a list of dictionaries
    # retrieve or create an open ClinVar submission:
    subm = store.get_open_clinvar_submission(institute_id)
    # save submission objects in submission:
    result = store.add_to_submission(subm["_id"], (variant_data, casedata_list))
    if result:
        flash("An open ClinVar submission was updated correctly with submitted data", "success")
    return redirect(url_for("cases.case", institute_id=institute_id, case_name=case_name))


@blueprint.route("/<institute_id>/clinvar_submissions", methods=["GET"])
def clinvar_submissions(institute_id):
    """Handle clinVar submission objects and files"""

    institute_obj = institute_and_case(store, institute_id)

    data = {
        "submissions": store.clinvar_submissions(institute_id),
        "institute": institute_obj,
        "variant_header_fields": CLINVAR_HEADER,
        "casedata_header_fields": CASEDATA_HEADER,
    }
    return render_template("clinvar_submissions.html", **data)


@blueprint.route("/<submission>/<case>/rename/<old_name>", methods=["POST"])
def clinvar_rename_casedata(submission, case, old_name):
    """Rename one or more casedata individuals belonging to the same clinvar submission, same case"""

    new_name = request.form.get("new_name")
    controllers.update_clinvar_sample_names(submission, case, old_name, new_name)
    return redirect(request.referrer + f"#cdata_{submission}")


@blueprint.route("/<submission>/<object_type>", methods=["POST"])
def clinvar_delete_object(submission, object_type):
    """Delete a single object (variant_data or case_data) associated with a clinvar submission"""

    store.delete_clinvar_object(
        object_id=request.form.get("delete_object"),
        object_type=object_type,
        submission_id=submission,
    )
    return redirect(request.referrer)


@blueprint.route("/<institute_id>/<submission>/update_status", methods=["POST"])
def clinvar_update_submission(institute_id, submission):
    """Update a submission status to open/closed, register an official SUB number or delete the entire submission"""

    controllers.update_clinvar_submission_status(request, institute_id, submission)
    return redirect(request.referrer)
