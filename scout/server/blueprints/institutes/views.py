# -*- coding: utf-8 -*-
import logging

from flask import Blueprint, render_template, flash, redirect, request, Response
from flask_login import current_user
from werkzeug.datastructures import Headers

from . import controllers
from scout.constants import PHENOTYPE_GROUPS, CASEDATA_HEADER, CLINVAR_HEADER
from scout.server.extensions import store
from scout.server.utils import user_institutes, templated, institute_and_case
from .forms import InstituteForm

LOG = logging.getLogger(__name__)

blueprint = Blueprint("overview", __name__, template_folder="templates")


@blueprint.route("/overview")
def institutes():
    """Display a list of all user institutes."""
    institute_objs = user_institutes(store, current_user)
    institutes = []
    for ins_obj in institute_objs:
        sanger_recipients = []
        for user_mail in ins_obj.get("sanger_recipients", []):
            user_obj = store.user(user_mail)
            if not user_obj:
                continue
            sanger_recipients.append(user_obj["name"])
        institutes.append(
            {
                "display_name": ins_obj["display_name"],
                "internal_id": ins_obj["_id"],
                "coverage_cutoff": ins_obj.get("coverage_cutoff", "None"),
                "sanger_recipients": sanger_recipients,
                "frequency_cutoff": ins_obj.get("frequency_cutoff", "None"),
                "phenotype_groups": ins_obj.get("phenotype_groups", PHENOTYPE_GROUPS),
                "case_count": sum(1 for i in store.cases(collaborator=ins_obj["_id"])),
            }
        )

    data = dict(institutes=institutes)
    return render_template("overview/institutes.html", **data)


@blueprint.route("/overview/edit/<institute_id>", methods=["GET", "POST"])
def institute(institute_id):
    """ Edit institute data """
    if institute_id not in current_user.institutes and current_user.is_admin is False:
        flash(
            "Current user doesn't have the permission to modify this institute", "warning",
        )
        return redirect(request.referrer)

    institute_obj = store.institute(institute_id)
    form = InstituteForm(request.form)

    # if institute is to be updated
    if request.method == "POST" and form.validate_on_submit():
        institute_obj = controllers.update_institute_settings(store, institute_obj, request.form)
        if isinstance(institute_obj, dict):
            flash("institute was updated ", "success")
        else:  # an error message was retuned
            flash(institute_obj, "warning")
            return redirect(request.referrer)

    data = controllers.institute(store, institute_id)
    # get all other institutes to populate the select of the possible collaborators
    institutes_tuples = []
    for inst in store.institutes():
        if not inst["_id"] == institute_id:
            institutes_tuples.append(((inst["_id"], inst["display_name"])))

    form.display_name.default = institute_obj.get("display_name")
    form.institutes.choices = institutes_tuples
    form.coverage_cutoff.default = institute_obj.get("coverage_cutoff")
    form.frequency_cutoff.default = institute_obj.get("frequency_cutoff")

    # collect all available default HPO terms
    default_phenotypes = [choice[0].split(" ")[0] for choice in form.pheno_groups.choices]
    if institute_obj.get("phenotype_groups"):
        for key, value in institute_obj["phenotype_groups"].items():
            if not key in default_phenotypes:
                custom_group = " ".join(
                    [key, ",", value.get("name"), "( {} )".format(value.get("abbr"))]
                )
                form.pheno_groups.choices.append((custom_group, custom_group))

    return render_template(
        "/overview/institute.html", form=form, default_phenotypes=default_phenotypes, **data
    )


@blueprint.route("/<institute_id>/clinvar_submissions", methods=["GET", "POST"])
@templated("overview/clinvar_submissions.html")
def clinvar_submissions(institute_id):
    """Handle clinVar submission objects and files"""

    def generate_csv(header, lines):
        yield header + "\n"
        for line in lines:  # lines have already quoted fields
            yield line + "\n"

    if request.method == "POST":
        submission_id = request.form.get("submission_id")
        if request.form.get("update_submission"):
            controllers.update_clinvar_submission_status(
                store, request, institute_id, submission_id
            )
        elif request.form.get("delete_variant"):  # delete a variant from a submission
            store.delete_clinvar_object(
                object_id=request.form.get("delete_variant"),
                object_type="variant_data",
                submission_id=submission_id,
            )  # remove variant and associated_casedata
        elif request.form.get("delete_casedata"):  # delete a case from a submission
            store.delete_clinvar_object(
                object_id=request.form.get("delete_casedata"),
                object_type="case_data",
                submission_id=submission_id,
            )  # remove just the casedata associated to a variant
        elif request.form.get("newSampleName"):
            # Rename one or more casedata samples
            controllers.update_clinvar_sample_names(
                store,
                submission_id,
                request.form.get("oldSampleName"),
                request.form["newSampleName"],
            )
        else:
            # Download submission CSV files (for variants or casedata)
            clinvar_file_data = controllers.clinvar_submission_file(store, request, submission_id)
            if clinvar_file_data is not None:
                headers = Headers()
                headers.add(
                    "Content-Disposition", "attachment", filename=clinvar_file_data[0],
                )
                return Response(
                    generate_csv(",".join(clinvar_file_data[1]), clinvar_file_data[2]),
                    mimetype="text/csv",
                    headers=headers,
                )

    institute_obj = institute_and_case(store, institute_id)

    data = {
        "submissions": controllers.clinvar_submissions(store, institute_id),
        "institute": institute_obj,
        "variant_header_fields": CLINVAR_HEADER,
        "casedata_header_fields": CASEDATA_HEADER,
    }
    return data
