# -*- coding: utf-8 -*-
import json
import logging

from bson import ObjectId
from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from werkzeug.datastructures import Headers

from scout.constants import CASEDATA_HEADER, CLINVAR_HEADER
from scout.server.blueprints.variants.controllers import update_form_hgnc_symbols
from scout.server.extensions import beacon, loqusdb, store
from scout.server.utils import institute_and_case, jsonconverter, templated
from scout.utils.scout_requests import post_request_json

from . import controllers
from .forms import GeneVariantFiltersForm, InstituteForm, PhenoModelForm, PhenoSubPanelForm

LOG = logging.getLogger(__name__)

blueprint = Blueprint(
    "overview",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/overview/static",
)


@blueprint.route("/api/v1/institutes", methods=["GET"])
def api_institutes():
    """API endpoint that returns institutes data"""
    data = dict(institutes=controllers.institutes())
    return jsonify(data)


@blueprint.route("/api/v1/institutes/<institute_id>/cases", methods=["GET", "POST"])
def api_cases(institute_id):
    """API endpoint that returns all cases for a given institute"""
    case_data = controllers.cases(store, request, institute_id)
    json_cases = json.dumps({"cases": case_data}, default=jsonconverter)
    return json_cases


@blueprint.route("/<institute_id>/cases", methods=["GET", "POST"])
@templated("overview/cases.html")
def cases(institute_id):
    """Display a list of cases for an institute."""
    return controllers.cases(store, request, institute_id)


@blueprint.route("/<institute_id>/causatives")
@templated("overview/causatives.html")
def causatives(institute_id):
    institute_obj = institute_and_case(store, institute_id)
    return controllers.causatives(institute_obj, request)


@blueprint.route("/<institute_id>/filters", methods=["GET"])
@templated("overview/filters.html")
def filters(institute_id):

    form = request.form

    institute_obj = institute_and_case(store, institute_id)

    filters = controllers.filters(store, institute_id)

    return dict(institute=institute_obj, form=form, filters=filters)


@blueprint.route("/<institute_id>/lock_filter/<filter_id>", methods=["POST"])
def lock_filter(institute_id, filter_id):

    filter_lock = request.form.get("filter_lock", "False")
    LOG.debug(
        "Attempting to toggle lock %s for %s with status %s",
        filter_id,
        institute_id,
        filter_lock,
    )

    if filter_lock == "True":
        filter_obj = controllers.unlock_filter(store, current_user, filter_id)

    if filter_lock == "False" or not filter_lock:
        filter_obj = controllers.lock_filter(store, current_user, filter_id)

    return redirect(request.referrer)


@blueprint.route("/<institute_id>/gene_variants", methods=["GET", "POST"])
@templated("overview/gene_variants.html")
def gene_variants(institute_id):
    """Display a list of SNV variants."""
    page = int(request.form.get("page", 1))

    institute_obj = institute_and_case(store, institute_id)

    data = {}

    if request.method == "GET":
        form = GeneVariantFiltersForm(request.args)
    else:  # POST
        form = GeneVariantFiltersForm(request.form)
        if form.variant_type.data == []:
            form.variant_type.data = ["clinical"]

        variant_type = form.data.get("variant_type")

        update_form_hgnc_symbols(store=store, case_obj=None, form=form)

        # If no valid gene is provided, redirect to form
        if not form.hgnc_symbols.data:
            flash("Provided gene symbols could not be used in variants' search", "warning")
            return redirect(request.referrer)

        variants_query = store.gene_variants(
            query=form.data,
            institute_id=institute_id,
            category="snv",
            variant_type=variant_type,
        )

        result_size = store.count_gene_variants(
            query=form.data,
            institute_id=institute_id,
            category="snv",
            variant_type=variant_type,
        )
        data = controllers.gene_variants(store, variants_query, result_size, page)

    return dict(institute=institute_obj, form=form, page=page, **data)


# MOST OF THE CONTENT OF THIS ENDPOINT WILL BE REMOVED AND INCLUDED INTO THE BEACON EXTENSION UNDER SERVER/EXTENSIONS
@blueprint.route("/overview/<institute_id>/add_beacon_dataset", methods=["POST"])
def add_beacon_dataset(institute_id):
    """Add a dataset to Beacon for a given institute"""
    if current_user.is_admin is False:
        flash(
            "Only an admin can create a new Beacon dataset",
            "warning",
        )
        return redirect(request.referrer)

    dataset_id = request.form.get("beacon_dataset")
    institute_obj = store.institute(institute_id)

    beacon.add_dataset(institute_obj, dataset_id)
    return redirect(request.referrer)


@blueprint.route("/overview/<institute_id>/settings", methods=["GET", "POST"])
def institute_settings(institute_id):
    """Show institute settings page"""

    if institute_id not in current_user.institutes and current_user.is_admin is False:
        flash(
            "Current user doesn't have the permission to modify this institute",
            "warning",
        )
        return redirect(request.referrer)

    institute_obj = store.institute(institute_id)
    institute_form = InstituteForm(request.form)

    beacon_form = controllers.populate_beacon_form(institute_obj)

    # if institute is to be updated
    if request.method == "POST" and institute_form.validate_on_submit():
        institute_obj = controllers.update_institute_settings(store, institute_obj, request.form)
        if isinstance(institute_obj, dict):
            flash("institute was updated ", "success")
        else:  # an error message was retuned
            flash(institute_obj, "warning")
            return redirect(request.referrer)

    data = controllers.institute(store, institute_id)
    loqus_instances = loqusdb.loqus_ids if hasattr(loqusdb, "loqus_ids") else []
    default_phenotypes = controllers.populate_institute_form(institute_form, institute_obj)

    return render_template(
        "/overview/institute_settings.html",
        form=institute_form,
        beacon_form=beacon_form,
        default_phenotypes=default_phenotypes,
        loqus_instances=loqus_instances,
        panel=1,
        **data,
    )


@blueprint.route("/overview/<institute_id>/users", methods=["GET"])
def institute_users(institute_id):
    """Should institute users list"""

    if institute_id not in current_user.institutes and current_user.is_admin is False:
        flash(
            "Current user doesn't have the permission to modify this institute",
            "warning",
        )
        return redirect(request.referrer)
    data = controllers.institute(store, institute_id)
    return render_template("/overview/users.html", panel=2, **data)


@blueprint.route("/<submission>/<case>/rename/<old_name>", methods=["POST"])
def clinvar_rename_casedata(submission, case, old_name):
    """Rename one or more casedata individuals belonging to the same clinvar submission, same case"""

    new_name = request.form.get("new_name")
    controllers.update_clinvar_sample_names(store, submission, case, old_name, new_name)
    return redirect(request.referrer + f"#cdata_{submission}")


@blueprint.route("/<institute_id>/<submission>/update_status", methods=["POST"])
def clinvar_update_submission(institute_id, submission):
    """Update a submission status to open/closed, register an official SUB number or delete the entire submission"""

    controllers.update_clinvar_submission_status(store, request, institute_id, submission)
    return redirect(request.referrer)


@blueprint.route("/<submission>/<object_type>", methods=["POST"])
def clinvar_delete_object(submission, object_type):
    """Delete a single object (variant_data or case_data) associated with a clinvar submission"""

    store.delete_clinvar_object(
        object_id=request.form.get("delete_object"),
        object_type=object_type,
        submission_id=submission,
    )
    return redirect(request.referrer)


@blueprint.route("/<submission>/download/<csv_type>/<clinvar_id>", methods=["GET"])
def clinvar_download_csv(submission, csv_type, clinvar_id):
    """Download a csv (Variant file or CaseData file) for a clinVar submission"""

    def generate_csv(header, lines):
        """Return downloaded header and lines with quoted fields"""
        yield header + "\n"
        for line in lines:
            yield line + "\n"

    clinvar_file_data = controllers.clinvar_submission_file(store, submission, csv_type, clinvar_id)

    if clinvar_file_data is None:
        return redirect(request.referrer)

    headers = Headers()
    headers.add("Content-Disposition", "attachment", filename=clinvar_file_data[0])
    return Response(
        generate_csv(",".join(clinvar_file_data[1]), clinvar_file_data[2]),
        mimetype="text/csv",
        headers=headers,
    )


@blueprint.route("/<institute_id>/clinvar_submissions", methods=["GET"])
@templated("overview/clinvar_submissions.html")
def clinvar_submissions(institute_id):
    """Handle clinVar submission objects and files"""

    institute_obj = institute_and_case(store, institute_id)

    data = {
        "submissions": controllers.clinvar_submissions(store, institute_id),
        "institute": institute_obj,
        "variant_header_fields": CLINVAR_HEADER,
        "casedata_header_fields": CASEDATA_HEADER,
    }
    return data


@blueprint.route("/<institute_id>/advanced_phenotypes", methods=["GET", "POST"])
@templated("overview/phenomodels.html")
def advanced_phenotypes(institute_id):
    """Show institute-level advanced phenotypes"""
    institute_obj = institute_and_case(store, institute_id)

    # Get a list of all users which are registered to this institute or collaborate with it
    collaborators = set()
    for inst_id in [institute_id] + institute_obj.get("collaborators", []):
        for user in store.users(institute=inst_id):
            if (
                user["email"] == current_user.email
            ):  # Do not include current user among collaborators
                continue
            collaborators.add((user["email"], user["name"], inst_id))

    if request.form.get("create_model"):  # creating a new phenomodel
        store.create_phenomodel(
            institute_id, request.form.get("model_name"), request.form.get("model_desc")
        )

    pheno_form = PhenoModelForm(request.form or None)
    phenomodels = list(store.phenomodels(institute_id=institute_id))

    data = {
        "institute": institute_obj,
        "collaborators": collaborators,
        "pheno_form": pheno_form,
        "phenomodels": phenomodels,
    }
    return data


@blueprint.route("/advanced_phenotypes/lock", methods=["POST"])
def lock_phenomodel():
    """Lock or unlock a specific phenomodel for editing"""
    form = request.form
    model_id = form.get("model_id")
    phenomodel_obj = store.phenomodel(model_id)
    if phenomodel_obj is None:
        return redirect(request.referrer)

    phenomodel_obj["admins"] = []
    if (
        "lock" in form
    ):  # lock phenomodel for all users except current user and specified collaborators
        phenomodel_obj["admins"] = [current_user.email] + form.getlist("user_admins")

    # update phenomodels admins:
    store.update_phenomodel(model_id, phenomodel_obj)
    return redirect(request.referrer)


@blueprint.route("/advanced_phenotypes/remove", methods=["POST"])
def remove_phenomodel():
    """Remove an entire phenomodel using its id"""
    model_id = request.form.get("model_id")
    model_obj = store.phenomodel_collection.find_one_and_delete({"_id": ObjectId(model_id)})
    if model_obj is None:
        flash(f"An error occurred while deleting phenotype model", "warning")
    return redirect(request.referrer)


@blueprint.route("/<institute_id>/phenomodel/<model_id>/edit_subpanel", methods=["POST"])
def checkbox_edit(institute_id, model_id):
    """Add or delete a single checkbox in a phenotyoe subpanel"""
    controllers.edit_subpanel_checkbox(model_id, request.form)
    return redirect(url_for(".phenomodel", institute_id=institute_id, model_id=model_id))


@blueprint.route("/<institute_id>/phenomodel/<model_id>", methods=["GET", "POST"])
@templated("overview/phenomodel.html")
def phenomodel(institute_id, model_id):
    """View/Edit an advanced phenotype model"""
    institute_obj = institute_and_case(store, institute_id)

    pheno_form = PhenoModelForm(request.form)
    subpanel_form = PhenoSubPanelForm(request.form)
    hide_subpanel = True

    if request.method == "POST":
        # update an existing phenotype model
        controllers.update_phenomodel(model_id, request.form)

    phenomodel_obj = store.phenomodel(model_id)
    if phenomodel_obj is None:
        flash(
            f"Could not retrieve given phenotype model using the given key '{model_id}'",
            "warning",
        )
        return redirect(request.referrer)

    pheno_form.model_name.data = phenomodel_obj["name"]
    pheno_form.model_desc.data = phenomodel_obj["description"]

    return dict(
        institute=institute_obj,
        pheno_form=pheno_form,
        phenomodel=phenomodel_obj,
        subpanel_form=subpanel_form,
    )
