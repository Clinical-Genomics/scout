import logging

from flask import Blueprint, render_template, request

from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from . import controllers

LOG = logging.getLogger(__name__)

clinvar_bp = Blueprint("clinvar", __name__, template_folder="templates")


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar", methods=["POST"])
def clinvar_create(institute_id, case_name):
    """Create a ClinVar submission document in database for one or more variants from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {"institute": institute_obj, "case": case_obj}
    pinned_selected = request.form.getlist("clinvar_variant")

    return render_template("clinvar_create.html", **data)
    """
    if request.form.get(
        "submit_pinned"
    ):  # Request received from case page, contains IDs of vars to export to CLinVar


        data = clinvar_export(store, institute_obj, case_obj, pinned_selected)
        return data

    # Request received from ClinVar page, contains complete info to save in ClinVar submission document
    build_clinvar_submission(store, request, institute_id, case_name)

    # Redirect to clinvar submissions handling page, to show the newest submission object
    return redirect(url_for("overview.clinvar_submissions", institute_id=institute_id))
    """
