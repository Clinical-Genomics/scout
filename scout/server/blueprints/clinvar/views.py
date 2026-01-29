import logging
from typing import List

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user

from scout.constants.clinvar import (
    CASEDATA_HEADER,
    CLINVAR_HEADER,
    GERMLINE_CLASSIF_TERMS,
    ONCOGENIC_CLASSIF_TERMS,
)
from scout.server.extensions import clinvar_api, store
from scout.server.utils import institute_and_case, safe_redirect_back

from . import controllers

LOG = logging.getLogger(__name__)

clinvar_bp = Blueprint(
    "clinvar",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/clinvar/static",
)


@clinvar_bp.route("/clinvar/status-enquiry/<submission_id>", methods=["POST"])
def clinvar_submission_status(submission_id):
    """Sends a request to ClinVar to retrieve and display the status of a submission."""

    # flash a message with current submission status for a ClinVar submission
    clinvar_resp_status = dict(
        clinvar_api.json_submission_status(
            submission_id=submission_id, api_key=request.form.get("apiKey")
        )
    )
    flash(
        f"Response from ClinVar: {clinvar_resp_status}",
        "primary",
    )
    return safe_redirect_back(request)


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar/add_germline_variant", methods=["POST"])
def clinvar_add_germline_variant(institute_id, case_name):
    """Add a germline variant to a germline submission object."""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {
        "institute": institute_obj,
        "case": case_obj,
        "germline_classif_terms": GERMLINE_CLASSIF_TERMS,
    }
    controllers.set_clinvar_form(request.form.get("var_id"), data)
    return render_template("clinvar/multistep_add_germline_variant.html", **data)


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar/clinvar_add_onc_variant", methods=["POST"])
def clinvar_add_onc_variant(institute_id: str, case_name: str):
    """Add an oncogenic variant to an oncogenicity submission object."""

    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {
        "institute": institute_obj,
        "case": case_obj,
        "onc_classif_terms": ONCOGENIC_CLASSIF_TERMS,
    }
    controllers.set_clinvar_form(request.form.get("var_id"), data)
    return render_template("clinvar/multistep_add_onc_variant.html", **data)


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar/save", methods=["POST"])
def clinvar_germline_save(institute_id: str, case_name: str):
    """Adds one germline variant with eventual observations to an open (or new) ClinVar submission."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    controllers.add_variant_to_submission(
        institute_obj=institute_obj, case_obj=case_obj, form=request.form, is_germline=True
    )
    return redirect(url_for("cases.case", institute_id=institute_id, case_name=case_name))


@clinvar_bp.route(
    "/<institute_id>/<case_name>/clinvar_onc/clinvar_save_onc_variant", methods=["POST"]
)
def clinvar_onc_save(institute_id: str, case_name: str):
    """Adds one oncogenic variant with eventual observations to an open (or new) ClinVar ongenicity submission."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    controllers.add_variant_to_submission(
        institute_obj=institute_obj, case_obj=case_obj, form=request.form, is_germline=False
    )
    return redirect(url_for("cases.case", institute_id=institute_id, case_name=case_name))


@clinvar_bp.route("/<institute_id>/clinvar_germline_submissions", methods=["GET"])
def clinvar_germline_submissions(institute_id):
    """Handle germline ClinVar submissions."""

    institute_obj = institute_and_case(store, institute_id)
    institute_clinvar_submitters: List[str] = institute_obj.get("clinvar_submitters", [])
    clinvar_id_filter = (
        request.args.get("clinvar_id_filter").strip()
        if request.args.get("clinvar_id_filter")
        else None
    )
    submissions = list(store.get_clinvar_submissions(institute_id=institute_id, type="germline"))
    deprecated_submissions = store.get_deprecated_clinvar_germline_submissions(
        institute_id, clinvar_id_filter=clinvar_id_filter
    )
    if deprecated_submissions:
        store.deprecate_type_none_germline_submissions()

    data = {
        "submissions": submissions + deprecated_submissions,
        "institute": institute_obj,
        "variant_header_fields": CLINVAR_HEADER,
        "casedata_header_fields": CASEDATA_HEADER,
        "show_submit": current_user.email in institute_clinvar_submitters
        or not institute_clinvar_submitters,
        "clinvar_id_filter": clinvar_id_filter,
    }
    return render_template("clinvar/clinvar_germline_submissions.html", **data)


@clinvar_bp.route("/<institute_id>/clinvar_onc_submissions", methods=["GET"])
def clinvar_onc_submissions(institute_id):
    """Handle clinVar submission objects and files"""

    institute_obj = institute_and_case(store, institute_id)
    institute_clinvar_submitters: List[str] = institute_obj.get("clinvar_submitters", [])
    data = {
        "submissions": list(
            store.get_clinvar_submissions(institute_id=institute_id, type="oncogenicity")
        ),
        "institute": institute_obj,
        "show_submit": current_user.email in institute_clinvar_submitters
        or not institute_clinvar_submitters,
    }
    return render_template("clinvar/clinvar_onc_submissions.html", **data)


@clinvar_bp.route("/<submission_id>/<submission_type>/delete_variant", methods=["POST"])
def clinvar_delete_variant(submission_id: str, submission_type: str):
    """Delete a single variant from a ClinVar submission document."""
    store.delete_variant_from_submission(
        submission_id=submission_id,
        variant_id=request.form.get("delete_object"),
        type=submission_type,
    )
    return safe_redirect_back(request)


@clinvar_bp.route("/<submission>/<object_type>", methods=["POST"])
def clinvar_delete_object(submission: str, object_type: str):
    """Delete a single object (variant_data or case_data) associated with a DEPRECATED ClinVar submission object."""

    controllers.remove_item_from_submission(
        submission=submission,
        object_type=object_type,
        subm_variant_id=request.form.get("delete_object"),
    )
    return safe_redirect_back(request)


@clinvar_bp.route("/<institute_id>/<submission>/update_status", methods=["POST"])
def clinvar_update_submission(institute_id, submission):
    """Update a submission status to open/closed, register an official SUB number or delete the entire submission"""
    controllers.update_clinvar_submission_status(request, institute_id, submission)
    return safe_redirect_back(request)


@clinvar_bp.route("/<submission>/<subm_type>/download", methods=["GET"])
def get_submission_as_json(submission, subm_type) -> dict:
    """Returns a json file for a clinVar submission."""

    data = store.get_json_submission(submission, subm_type)
    if data is None:
        abort(404, "Submission not found")
    return data


@clinvar_bp.route("/<institute_id>/<submission>/<subm_type>/send", methods=["POST"])
def send_api_submission(institute_id, submission, subm_type):
    """Send a submission object to ClinVar using the API."""
    institute_obj = institute_and_case(store, institute_id)

    json_subm_obj = store.get_json_submission(submission=submission, subm_type=subm_type)
    if not json_subm_obj:
        return safe_redirect_back(request)

    service_url, code, submit_res = clinvar_api.submit_json(
        json_subm_obj, request.form.get("apiKey")
    )

    if code in [200, 201]:
        clinvar_id = submit_res.json().get("id")
        flash(
            f"Submission sent to API URL '{service_url}'. Submitted with ID: {clinvar_id}. Please wait a few minutes before checking its status.",
            "success",
        )
        # Update ClinVar submission ID with the ID returned from ClinVar
        store.update_clinvar_id(
            clinvar_id=clinvar_id,
            submission_id=submission_id,
        )
        # Update submission status as submitted
        store.update_clinvar_submission_status(
            institute_id=institute_id, submission_id=submission_id, status="submitted"
        )
    else:
        flash(
            f"Submission sent to API URL '{service_url}'. Returned error {code}: {submit_res.json()}",
            "warning",
        )

    return safe_redirect_back(request)
