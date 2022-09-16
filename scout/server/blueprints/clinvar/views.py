import logging

from flask import Blueprint, render_template, request

from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from . import controllers

LOG = logging.getLogger(__name__)

clinvar_bp = Blueprint("clinvar", __name__, template_folder="templates")


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar", methods=["POST"])
def clinvar_add_variant(institute_id, case_name):
    """Create a ClinVar submission document in database for one or more variants from a case."""
    institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    data = {"institute": institute_obj, "case": case_obj}
    controllers.set_clinvar_form(request.form.get("var_id"), data)
    return render_template("clinvar_add_one.html", **data)


@clinvar_bp.route("/<institute_id>/<case_name>/clinvar_add_var", methods=["POST"])
def add_variant(institute_id, case_name):
    """Adds one variant to an open ClinVar submission"""

    variant_data = controllers.parse_variant_form_fields(request.form)  # dictionary
    casedata_list = controllers.parse_casedata_form_fields(request.form)  # a list of dictionaries
    LOG.warning(variant_data)
    LOG.error(casedata_list)
    return request.form
