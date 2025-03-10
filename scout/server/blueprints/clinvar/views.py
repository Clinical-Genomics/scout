import logging
from json import dumps
from tempfile import NamedTemporaryFile
from typing import List, Tuple

from flask import (
    Blueprint,
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
)
from scout.server.extensions import clinvar_api, store
from scout.server.utils import institute_and_case

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
    flash(
        f'Response from ClinVar: {clinvar_api.json_submission_status( submission_id=submission_id, api_key=request.form.get("apiKey"))}',
        "primary",
    )
    return redirect(request.referrer)


@clinvar_bp.route("/clinvar/delete-enquiry/<submission_id>", methods=["POST"])
def clinvar_submission_delete(submission_id):
    """Sends a request to ClinVar to delete a successfully processed submission."""

    # Retrieve the actual submission status:
    delete_res: Tuple[int, dict] = clinvar_api.delete_clinvar_submission(
        submission_id=submission_id, api_key=request.form.get("apiKey")
    )
    flash(
        f"ClinVar response: { str(delete_res[1]) }",
        "success" if delete_res[0] == 201 else "warning",
    )
    return redirect(request.referrer)


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar/add_variant", methods=["POST"])
def clinvar_add_variant(institute_id, case_name):
    """Create a ClinVar submission document in database for one or more variants from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {
        "institute": institute_obj,
        "case": case_obj,
        "germline_classif_terms": GERMLINE_CLASSIF_TERMS,
        "max_validated_hgvs": controllers.MAX_VALIDATED_HGVS,
    }
    controllers.set_clinvar_form(request.form.get("var_id"), data)
    return render_template("clinvar/multistep_add_variant.html", **data)


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar/save", methods=["POST"])
def clinvar_save(institute_id, case_name):
    """Adds one variant with eventual CaseData observations to an open (or new) ClinVar submission"""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    controllers.add_variant_to_submission(
        institute_obj=institute_obj, case_obj=case_obj, form=request.form
    )
    return redirect(url_for("cases.case", institute_id=institute_id, case_name=case_name))


@clinvar_bp.route("/<institute_id>/clinvar_submissions", methods=["GET"])
def clinvar_submissions(institute_id):
    """Handle clinVar submission objects and files"""

    institute_obj = institute_and_case(store, institute_id)
    institute_clinvar_submitters: List[str] = institute_obj.get("clinvar_submitters", [])
    data = {
        "submissions": store.clinvar_submissions(institute_id),
        "institute": institute_obj,
        "variant_header_fields": CLINVAR_HEADER,
        "casedata_header_fields": CASEDATA_HEADER,
        "show_submit": current_user.email in institute_clinvar_submitters
        or not institute_clinvar_submitters,
    }
    return render_template("clinvar/clinvar_submissions.html", **data)


@clinvar_bp.route("/<submission>/<case>/rename/<old_name>", methods=["POST"])
def clinvar_rename_casedata(submission, case, old_name):
    """Rename one or more casedata individuals belonging to the same clinvar submission, same case"""

    new_name = request.form.get("new_name")
    controllers.update_clinvar_sample_names(submission, case, old_name, new_name)
    return redirect(request.referrer + f"#cdata_{submission}")


@clinvar_bp.route("/<submission>/<object_type>", methods=["POST"])
def clinvar_delete_object(submission: str, object_type: str):
    """Delete a single object (variant_data or case_data) associated with a ClinVar submission"""

    controllers.remove_item_from_submission(
        submission=submission,
        object_type=object_type,
        subm_variant_id=request.form.get("delete_object"),
    )
    return redirect(request.referrer)


@clinvar_bp.route("/<institute_id>/<submission>/update_status", methods=["POST"])
def clinvar_update_submission(institute_id, submission):
    """Update a submission status to open/closed, register an official SUB number or delete the entire submission"""
    controllers.update_clinvar_submission_status(request, institute_id, submission)
    return redirect(request.referrer)


@clinvar_bp.route("/<submission>/download/json/<clinvar_id>", methods=["GET"])
def clinvar_download_json(submission, clinvar_id):
    """Download a json for a clinVar submission"""

    code, conversion_res = controllers.json_api_submission(submission_id=submission)

    if code in [200, 201]:
        # Write temp CSV file and serve it in response
        tmp_json = NamedTemporaryFile(mode="a+", prefix=clinvar_id, suffix=".json")
        tmp_json.write(dumps(conversion_res, indent=4))

        tmp_json.flush()
        tmp_json.seek(0)
        return send_file(
            tmp_json.name,
            download_name=f"{clinvar_id}.json",
            mimetype="application/json",
            as_attachment=True,
        )
    else:
        flash(f"JSON file could not be crated for ClinVar submission: {clinvar_id} ", "warning")
        return redirect(request.referrer)
