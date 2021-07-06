# -*- coding: utf-8 -*-
import datetime
import logging

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from flask_weasyprint import HTML, render_pdf

from scout.server.extensions import store
from scout.server.utils import templated, user_institutes

from . import controllers
from .forms import PanelGeneForm

LOG = logging.getLogger(__name__)
panels_bp = Blueprint("panels", __name__, template_folder="templates")


@panels_bp.route("/panels", methods=["GET", "POST"])
@templated("panels/panels.html")
def panels():
    """Show all panels for a case."""
    if request.method == "POST":
        # update an existing panel
        csv_file = request.files["csv_file"]
        content = csv_file.stream.read()
        lines = None
        try:
            if b"\n" in content:
                lines = content.decode("utf-8-sig", "ignore").split("\n")
            else:
                lines = content.decode("windows-1252").split("\r")
        except Exception as err:
            flash(
                "Something went wrong while parsing the panel CSV file! ({})".format(err),
                "danger",
            )
            return redirect(request.referrer)

        new_panel_name = request.form.get("new_panel_name")
        if new_panel_name:  # create a new panel
            new_panel_id = controllers.new_panel(
                store=store,
                institute_id=request.form["institute"],
                panel_name=new_panel_name,
                display_name=request.form["display_name"] or new_panel_name.replace("_", " "),
                csv_lines=lines,
                maintainer=[current_user._id],
                description=request.form["description"],
            )
            if new_panel_id is None:
                return redirect(request.referrer)

            flash("new gene panel added, {}!".format(new_panel_name), "success")
            return redirect(url_for("panels.panel", panel_id=new_panel_id))

        # modify an existing panel
        update_option = request.form["modify_option"]

        panel_obj = store.gene_panel(request.form["panel_name"])
        if panel_obj is None:
            return abort(404, "gene panel not found: {}".format(request.form["panel_name"]))

        if panel_write_granted(panel_obj, current_user):
            panel_obj = controllers.update_panel(
                store=store,
                panel_name=request.form["panel_name"],
                csv_lines=lines,
                option=update_option,
            )
        else:
            flash(
                "Permission denied: please ask a panel maintainer or admin for help.",
                "danger",
            )

        return redirect(url_for("panels.panel", panel_id=panel_obj["_id"]))

    institutes = list(user_institutes(store, current_user))
    panel_names = [
        name
        for institute in institutes
        for name in store.gene_panels(institute_id=institute["_id"]).distinct("panel_name")
    ]

    panel_versions = {}
    for name in panel_names:
        panel_versions[name] = store.gene_panels(panel_id=name)

    panel_groups = []
    for institute_obj in institutes:
        institute_panels = store.latest_panels(institute_obj["_id"])
        panel_groups.append((institute_obj, institute_panels))

    return dict(
        panel_groups=panel_groups,
        panel_names=panel_names,
        panel_versions=panel_versions,
        institutes=institutes,
    )


def panel_write_granted(panel_obj, user):
    return (
        not panel_obj.get("maintainer") or user.is_admin or user._id in panel_obj.get("maintainer")
    )


@panels_bp.route("/panels/<panel_id>", methods=["GET", "POST"])
@templated("panels/panel.html")
def panel(panel_id):
    """Display (and add pending updates to) a specific gene panel."""
    panel_obj = store.gene_panel(panel_id) or store.panel(panel_id)

    if request.method == "POST":
        if request.form.get("update_description"):
            panel_obj["description"] = request.form["panel_description"]

            if panel_write_granted(panel_obj, current_user):
                store.update_panel(panel_obj=panel_obj)
            else:
                flash(
                    "Permission denied: please ask a panel maintainer or admin for help.",
                    "danger",
                )
            return redirect(url_for("panels.panel", panel_id=panel_obj["_id"]))

        raw_hgnc_id = request.form["hgnc_id"]
        if "|" in raw_hgnc_id:
            raw_hgnc_id = raw_hgnc_id.split(" | ", 1)[0]
        hgnc_id = 0
        try:
            hgnc_id = int(raw_hgnc_id)
        except ValueError:
            flash("Provided HGNC is not valid : '{}'".format(raw_hgnc_id), "danger")
            return redirect(request.referrer)
        action = request.form["action"]
        gene_obj = store.hgnc_gene(hgnc_identifier=hgnc_id, build="37") or store.hgnc_gene(
            hgnc_identifier=hgnc_id, build="38"
        )
        if gene_obj is None:
            flash("HGNC id not found: {}".format(hgnc_id), "warning")
            return redirect(request.referrer)

        if action == "add":
            panel_gene = controllers.existing_gene(store, panel_obj, hgnc_id)
            if panel_gene:
                flash("gene already in panel: {}".format(panel_gene["symbol"]), "warning")
            else:
                # ask user to fill-in more information about the gene
                return redirect(url_for(".gene_edit", panel_id=panel_id, hgnc_id=hgnc_id))
        elif action == "delete":
            LOG.debug("marking gene to be deleted: %s", hgnc_id)
            panel_obj = store.add_pending(panel_obj, gene_obj, action="delete")
    data = controllers.panel(store, panel_obj)
    if request.args.get("case_id"):
        data["case"] = store.case(request.args["case_id"])
    if request.args.get("institute_id"):
        data["institute"] = store.institute(request.args["institute_id"])
    return data


@panels_bp.route("/panels/<panel_id>/update", methods=["POST"])
def panel_update(panel_id):
    """Update panel to a new version."""
    panel_obj = store.panel(panel_id)
    if request.form.get("cancel_pending"):
        updated_panel = store.reset_pending(panel_obj)
        if updated_panel is None:
            flash("Couldn't find a panel with ID {}".format(panel_id), "warning")
        elif updated_panel.get("pending") is None:
            flash("Pending actions were correctly canceled!", "success")

        return redirect(request.referrer)

    if panel_write_granted(panel_obj, current_user):
        update_version = request.form.get("version", None)
        new_panel_id = store.apply_pending(panel_obj, update_version)
        panel_id = new_panel_id
    else:
        flash(
            "Permission denied: please ask a panel maintainer or admin for help.",
            "danger",
        )

    return redirect(url_for("panels.panel", panel_id=panel_id))


@panels_bp.route("/panels/export-panel/<panel_id>", methods=["GET", "POST"])
def panel_export(panel_id):
    """Export panel to PDF file"""
    panel_obj = store.panel(panel_id)
    data = controllers.panel_export(store, panel_obj)
    data["report_created_at"] = datetime.datetime.now().strftime("%Y-%m-%d")
    html_report = render_template("panels/panel_pdf_simple.html", **data)
    return render_pdf(
        HTML(string=html_report),
        download_filename=data["panel"]["panel_name"]
        + "_"
        + str(data["panel"]["version"])
        + "_"
        + datetime.datetime.now().strftime("%Y-%m-%d")
        + "_scout.pdf",
    )


def tx_choices(hgnc_id, panel_obj):
    """Collect transcripts from a gene both in build 37 and 38

    Args:
        hgnc_id(int): a gene HGNC ID
        panel_obj(dict): a gene panel dictionary representation

    Returns:
        transcript_choices(list) a list with the options for a form select field
    """

    transcript_choices = []
    hgnc_gene = None

    for build in ["37", "38"]:
        build_specific_hgnc_gene = store.hgnc_gene(hgnc_identifier=hgnc_id, build=build)
        if build_specific_hgnc_gene is None:
            continue

        hgnc_gene = build_specific_hgnc_gene

        for transcript in build_specific_hgnc_gene["transcripts"]:
            if transcript.get("refseq_id"):
                refseq_id = transcript.get("refseq_id")
                transcript_choices.append((refseq_id, f"{refseq_id} (build {build})"))

    # collect even refseq version provided by user for this transcript (might have a version)
    if panel_obj.get("genes"):
        genes_dict = {gene_obj["symbol"]: gene_obj for gene_obj in panel_obj["genes"]}
        gene_obj = genes_dict.get(hgnc_gene["hgnc_symbol"])
        if gene_obj:
            for transcript in gene_obj.get("disease_associated_transcripts", []):
                if (transcript, transcript) not in transcript_choices:
                    transcript_choices.append((transcript, f"{transcript} (previous choice)"))
    return transcript_choices


@panels_bp.route("/panels/<panel_id>/update/<int:hgnc_id>", methods=["GET", "POST"])
@templated("panels/gene-edit.html")
def gene_edit(panel_id, hgnc_id):
    """Edit additional information about a panel gene."""

    panel_obj = store.panel(panel_id)
    hgnc_gene = store.hgnc_gene(hgnc_identifier=hgnc_id, build="37") or store.hgnc_gene(
        hgnc_identifier=hgnc_id, build="38"
    )
    panel_gene = controllers.existing_gene(store, panel_obj, hgnc_id)

    form = PanelGeneForm()

    form.disease_associated_transcripts.choices = tx_choices(hgnc_id, panel_obj)
    if form.validate_on_submit():
        action = "edit" if panel_gene else "add"
        info_data = form.data.copy()
        if "csrf_token" in info_data:
            del info_data["csrf_token"]
        if info_data["custom_inheritance_models"] != "":
            info_data["custom_inheritance_models"] = info_data["custom_inheritance_models"].split(
                ","
            )

        store.add_pending(panel_obj, hgnc_gene, action=action, info=info_data)
        return redirect(url_for(".panel", panel_id=panel_id))

    if panel_gene:
        form.custom_inheritance_models.data = ", ".join(
            panel_gene.get("custom_inheritance_models", [])
        )
        for field_key in [
            "disease_associated_transcripts",
            "reduced_penetrance",
            "mosaicism",
            "inheritance_models",
            "custom_inheritance_models",
            "database_entry_version",
            "comment",
        ]:
            form_field = getattr(form, field_key)
            if not form_field.data:
                panel_value = panel_gene.get(field_key)
                if panel_value is not None:
                    form_field.process_data(panel_value)
    return dict(panel=panel_obj, form=form, gene=hgnc_gene, panel_gene=panel_gene)
