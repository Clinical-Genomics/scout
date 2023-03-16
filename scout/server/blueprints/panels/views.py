# -*- coding: utf-8 -*-
import datetime
import json
import logging

from flask import (
    Blueprint,
    Response,
    escape,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user

from scout.constants import DATE_DAY_FORMATTER
from scout.export.panel import export_gene_panels
from scout.server.blueprints.cases.controllers import check_outdated_gene_panel
from scout.server.extensions import store
from scout.server.utils import (
    html_to_pdf_file,
    institute_and_case,
    jsonconverter,
    public_endpoint,
    templated,
    user_institutes,
)
from scout.utils.gene import parse_raw_gene_ids

from . import controllers
from .forms import PanelGeneForm

LOG = logging.getLogger(__name__)
panels_bp = Blueprint("panels", __name__, template_folder="templates")


@panels_bp.route("/api/v1/panels/<panel_name>", methods=["GET", "POST"])
@public_endpoint
def api_panels(panel_name):
    """Return JSON data about panels with a given panel name.
    Returns all versions.
    """
    json_out = controllers.get_panels(store, panel_name)

    return Response(json.dumps(json_out, default=jsonconverter), mimetype="application/json")


@panels_bp.route("/panels", methods=["GET", "POST"])
@templated("panels/panels.html")
def panels():
    """Show all panels for a user"""

    # Add search box and add results if applicable
    panels_found = []
    search_string = ""
    if request.method == "POST" and request.form.get("search_for"):
        # Query db for panels containing the search string. This is done with autocompletion
        # therefor only one(1) hgnc_id will be received from the form.
        hgnc_symbols = []
        search_string = escape(request.form.get("search_for"))
        try:
            hgnc_symbols = parse_raw_gene_ids([search_string])
            hgnc_id = hgnc_symbols.pop()
        except ValueError:
            flash(
                "Provided gene info could not be parsed! " "Please allow autocompletion to finish.",
                "warning",
            )
        panels_found = store.search_panels_hgnc_id(hgnc_id)

    # Add new panel
    elif request.method == "POST":
        # Edit/create a new panel and redirect to its page
        redirect_panel_id = controllers.panel_create_or_update(store, request)
        if redirect_panel_id:
            return redirect(url_for("panels.panel", panel_id=redirect_panel_id))

        return redirect(url_for("panels.panels"))

    institutes = list(user_institutes(store, current_user))
    panel_names = [
        name
        for institute in institutes
        for name in store.gene_panels(institute_id=institute["_id"], include_hidden=True).distinct(
            "panel_name"
        )
    ]
    panel_versions = {}
    for name in panel_names:
        panels = store.gene_panels(panel_id=name, include_hidden=True)
        panel_versions[name] = [
            panel_obj
            for panel_obj in panels
            if controllers.shall_display_panel(panel_obj, current_user)
        ]
    panel_groups = []
    for institute_obj in institutes:
        institute_panels = (
            panel_obj
            for panel_obj in store.latest_panels(institute_obj["_id"], include_hidden=True)
            if controllers.shall_display_panel(panel_obj, current_user)
        )
        panel_groups.append((institute_obj, institute_panels))
    return dict(
        panel_groups=panel_groups,
        panel_names=panel_names,
        panel_versions=panel_versions,
        institutes=institutes,
        search_string=search_string,
        search_result=panels_found,
    )


@panels_bp.route("/panels/<panel_id>", methods=["GET", "POST"])
@templated("panels/panel.html")
def panel(panel_id):
    """Display (and add pending updates to) a specific gene panel."""

    panel_obj = store.gene_panel(panel_id) or store.panel(panel_id)
    if not panel_obj:
        flash("Panel with id {} not found.".format(panel_id), "warning")
        return redirect(url_for("panels.panels"))

    if request.method == "POST":
        if request.form.get("update_description"):
            panel_obj["description"] = request.form["panel_description"]

            if controllers.panel_write_granted(panel_obj, current_user):
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
        gene_obj = store.hgnc_gene_caption(
            hgnc_identifier=hgnc_id, build="37"
        ) or store.hgnc_gene_caption(hgnc_identifier=hgnc_id, build="38")
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
        case_obj = store.case(request.args["case_id"])

        case_obj["outdated_panels"] = {}
        panel_name = panel_obj["panel_name"]
        latest_panel = store.gene_panel(panel_name)
        if panel_obj["version"] < latest_panel["version"]:
            extra_genes, missing_genes = check_outdated_gene_panel(panel_obj, latest_panel)
            if extra_genes or missing_genes:
                case_obj["outdated_panels"][panel_name] = {
                    "missing_genes": missing_genes,
                    "extra_genes": extra_genes,
                }

        data["case"] = case_obj

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

    if controllers.panel_write_granted(panel_obj, current_user):
        update_version = request.form.get("version", None)
        new_panel_id = store.apply_pending(panel_obj, update_version)
        panel_id = new_panel_id
    else:
        flash(
            "Permission denied: please ask a panel maintainer or admin for help.",
            "danger",
        )

    return redirect(url_for("panels.panel", panel_id=panel_id))


@panels_bp.route("/panels/<panel_id>/delete", methods=["POST"])
def panel_delete(panel_id):
    """Remove an existing panel."""
    panel_obj = store.gene_panel(panel_id) or store.panel(panel_id)
    if panel_obj is None:
        flash(
            f"Panel object with id '{panel_id}' was not found.",
            "danger",
        )
        return redirect(request.referrer)

    if controllers.panel_write_granted(panel_obj, current_user):
        LOG.info("Mark gene panel: %s as deleted (hidden)" % panel_obj["display_name"])
        panel_obj["hidden"] = True
        store.update_panel(panel_obj=panel_obj)
        flash("Removed gene panel: %s" % panel_obj["display_name"], "success")
    else:
        flash(
            "Permission denied: please ask a panel maintainer or admin for help.",
            "danger",
        )
    return redirect(url_for("panels.panels", panel_id=panel_obj["_id"]))


@panels_bp.route("/panels/<panel_id>/restore", methods=["POST"])
def panel_restore(panel_id):
    """Remove an existing panel."""
    panel_obj = store.panel(panel_id)
    # abort when trying to hide an already hidden panel
    if controllers.panel_write_granted(panel_obj, current_user):
        panel_obj["hidden"] = False
        store.update_panel(panel_obj=panel_obj)
        flash("Restored gene panel: %s" % panel_obj["display_name"], "success")
    else:
        flash(
            "Permission denied: please ask a panel maintainer or admin for help.",
            "danger",
        )
    return redirect(url_for("panels.panels", panel_id=panel_obj["_id"]))


@panels_bp.route("/panels/export-panel-txt/<panel_id>", methods=["GET"])
def panel_export_txt(panel_id):
    """Download a gene panel in txt format"""
    panel_obj = store.panel(panel_id)
    file_name = controllers.downloaded_panel_name(panel_obj=panel_obj, format="txt")

    lines = export_gene_panels(
        adapter=store,
        panels=[panel_obj["panel_name"]],
        version=panel_obj["version"],
    )

    def generate():
        for row in lines:
            yield f"{row}\n"

    return Response(
        generate(),
        mimetype="text/txt",
        headers={"Content-Disposition": f"attachment;filename={file_name}"},
    )


@panels_bp.route("/panels/export-panel-pdf/<panel_id>", methods=["GET"])
def panel_export_pdf(panel_id):
    """Export panel to PDF file"""
    panel_obj = store.panel(panel_id)
    data = controllers.panel_data(store, panel_obj)
    data["report_created_at"] = datetime.datetime.now().strftime(DATE_DAY_FORMATTER)
    html_report = render_template("panels/panel_pdf_simple.html", **data)

    bytes_file = html_to_pdf_file(html_report, "portrait", 300)
    file_name = controllers.downloaded_panel_name(panel_obj=panel_obj, format="pdf")
    return send_file(
        bytes_file,
        download_name=file_name,
        mimetype="application/pdf",
        as_attachment=True,
    )


@panels_bp.route("/panels/export-panel-case_hits/<panel_id>", methods=["POST"])
def panel_export_case_hits(panel_id):
    """Export panel genes and case-specific hits in STRs and SMN variant categories to PDF file"""
    institute_obj = None
    case_obj = None

    try:
        institute_id, case_name = request.form.get("case_name").strip().split(" - ")
    except ValueError:
        flash(
            "Could not parse case name, please use format: 'cust000 - 643594' or use typing suggestions",
            "warning",
        )
        return redirect(request.referrer)
    try:
        institute_obj, case_obj = institute_and_case(store, institute_id, case_name)
    except Exception:
        flash(
            f"Could not find a case named '{case_name}' associated to institute '{institute_id}'",
            "warning",
        )
        return redirect(request.referrer)
    data = controllers.panel_export_case_hits(panel_id, institute_obj, case_obj)
    now = datetime.datetime.now().strftime(DATE_DAY_FORMATTER)
    data["report_created_at"] = now
    html_report = render_template("panels/panel_pdf_case_hits.html", **data)
    bytes_file = html_to_pdf_file(html_report, "portrait", 300)
    file_name = "_".join(
        [
            data["panel"]["panel_name"],
            str(data["panel"]["version"]),
            institute_id,
            case_name,
            now,
            "scout.pdf",
        ]
    )
    return send_file(
        bytes_file,
        download_name=file_name,
        mimetype="application/pdf",
        as_attachment=True,
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
    hgnc_gene = store.hgnc_gene_caption(
        hgnc_identifier=hgnc_id, build="37"
    ) or store.hgnc_gene_caption(hgnc_identifier=hgnc_id, build="38")
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
        custom_models = [
            model for model in panel_gene.get("custom_inheritance_models", []) if model != ""
        ]
        if custom_models:
            form.custom_inheritance_models.data = ", ".join(
                panel_gene.get("custom_inheritance_models")
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
