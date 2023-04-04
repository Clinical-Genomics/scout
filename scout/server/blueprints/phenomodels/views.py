from bson import ObjectId
from flask import Blueprint, flash, redirect, request, url_for
from flask_login import current_user

from scout.server.extensions import store
from scout.server.utils import institute_and_case, templated

from . import controllers
from .forms import PhenoModelForm, PhenoSubPanelForm

phenomodels_bp = Blueprint(
    "phenomodels",
    __name__,
    static_folder="static",
    static_url_path="/phenomodels/static",
    template_folder="templates",
)


@phenomodels_bp.route("/<institute_id>/advanced_phenotypes", methods=["GET"])
@templated("phenomodels.html")
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

    pheno_form = PhenoModelForm()
    phenomodels = list(store.phenomodels(institute_id=institute_id))

    data = {
        "institute": institute_obj,
        "collaborators": collaborators,
        "pheno_form": pheno_form,
        "phenomodels": phenomodels,
    }
    return data


@phenomodels_bp.route("/<institute_id>/create_phenomodel", methods=["POST"])
def create_phenomodel(institute_id):
    """Create a new phenomodel"""
    institute_and_case(store, institute_id)
    store.create_phenomodel(
        institute_id, request.form.get("model_name"), request.form.get("model_desc")
    )
    return redirect(request.referrer)


@phenomodels_bp.route("/advanced_phenotypes/lock", methods=["POST"])
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


@phenomodels_bp.route("/advanced_phenotypes/remove", methods=["POST"])
def remove_phenomodel():
    """Remove an entire phenomodel using its id"""
    model_id = request.form.get("model_id")
    model_obj = store.phenomodel_collection.find_one_and_delete({"_id": ObjectId(model_id)})
    if model_obj is None:
        flash("An error occurred while deleting phenotype model", "warning")
    return redirect(request.referrer)


@phenomodels_bp.route("/<institute_id>/phenomodel/<model_id>/edit_subpanel", methods=["POST"])
def checkbox_edit(institute_id, model_id):
    """Add or delete a single checkbox in a phenotyoe subpanel"""
    controllers.edit_subpanel_checkbox(model_id, request.form)
    return redirect(url_for(".phenomodel", institute_id=institute_id, model_id=model_id))


@phenomodels_bp.route("/<institute_id>/phenomodel-edit/<model_id>", methods=["POST"])
def phenomodel_edit(institute_id, model_id):
    """Edit a phenomodel or a subpanel"""
    institute_and_case(store, institute_id)
    controllers.update_phenomodel(model_id, request.form)
    return redirect(request.referrer)


@phenomodels_bp.route("/<institute_id>/phenomodel/<model_id>", methods=["GET"])
@templated("phenomodel.html")
def phenomodel(institute_id, model_id):
    """View/Edit an advanced phenotype model"""
    institute_obj = institute_and_case(store, institute_id)

    phenomodel_obj = store.phenomodel(model_id)
    if phenomodel_obj is None:
        flash(
            f"Could not retrieve given phenotype model using the given key '{model_id}'",
            "warning",
        )
        return redirect(request.referrer)

    pheno_form = PhenoModelForm()
    subpanel_form = PhenoSubPanelForm()
    pheno_form.model_name.data = phenomodel_obj["name"]
    pheno_form.model_desc.data = phenomodel_obj["description"]

    return dict(
        institute=institute_obj,
        pheno_form=pheno_form,
        phenomodel=phenomodel_obj,
        subpanel_form=subpanel_form,
    )
