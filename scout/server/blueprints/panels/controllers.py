# -*- coding: utf-8 -*-
import datetime as dt
import logging

from flask import flash, redirect
from flask_login import current_user

from scout.build.panel import build_panel
from scout.constants import DATE_DAY_FORMATTER
from scout.parse.panel import parse_genes
from scout.server.blueprints.cases.controllers import check_outdated_gene_panel
from scout.server.extensions import store

LOG = logging.getLogger(__name__)

INHERITANCE_MODELS = ["ar", "ad", "mt", "xr", "xd", "x", "y"]


def shall_display_panel(panel_obj, user):
    """Check if panel shall be displayed based on display status and user previleges."""
    is_visible = not panel_obj.get("hidden", False)
    return is_visible or panel_write_granted(panel_obj, user)


def panel_write_granted(panel_obj, user):
    return any(
        ["maintainer" not in panel_obj, user.is_admin, user._id in panel_obj.get("maintainer", [])]
    )


def panel_decode_lines(panel_file):
    """Returns a provided gene panel file as single lines
    Accepts:
        panel_file (werkzeug.datastructures.FileStorage)
    Returns:
        lines(list): list of lines present in gene panel uploaded using the form
    """
    content = panel_file.stream.read()
    lines = None
    try:  # Try to read the csv or txt file containing genes info
        if b"\n" in content:
            lines = content.decode("utf-8-sig", "ignore").split("\n")
        else:
            lines = content.decode("windows-1252").split("\r")
    except Exception as err:
        flash(
            "Something went wrong while parsing the panel gene panel file! ({})".format(err),
            "danger",
        )
    return lines


def create_new_panel(store, request, lines):
    """Create a new gene panel with the data provided using the form

    Args:
        store(scout.adapter.MongoAdapter)
        request(flask.request) request sent by browser form to the /panels endpoint
        lines(list): list of lines containing gene data

    Returns:
        new_panel_id(str): the _id a newly created panel
    """
    new_panel_name = request.form.get("new_panel_name")
    new_panel_id = new_panel(
        store=store,
        institute_id=request.form["institute"],
        panel_name=new_panel_name,
        display_name=request.form["display_name"] or new_panel_name.replace("_", " "),
        csv_lines=lines,
        maintainer=[current_user._id],
        description=request.form["description"],
    )
    if new_panel_id is None:
        return None

    flash("New gene panel added: {}!".format(new_panel_name), "success")
    return new_panel_id


def update_existing_panel(store, request, lines):
    """Update an existing panel by replacing its genes of adding genes to the existing ones

    Args:
        store(scout.adapter.MongoAdapter)
        request(flask.request) request sent by browser form to the /panels endpoint
        lines(list): list of lines containing gene data

    Returns:
        panel_obj.get("_id") (str): the _id of the panel the used is editing
    """
    panel_name = request.form["panel_name"]
    update_option = request.form["modify_option"]

    panel_obj = store.gene_panel(panel_name)
    if panel_obj is None:
        return None

    if panel_write_granted(panel_obj, current_user):
        panel_obj = update_panel(
            store=store,
            panel_name=panel_name,
            csv_lines=lines,
            option=update_option,
        )
        if panel_obj:
            return panel_obj.get("_id")
    else:
        flash(
            "Permission denied: please ask a panel maintainer or admin for help.",
            "danger",
        )


def panel_create_or_update(store, request):
    """Process a user request to create a new gene panel

    Args:
        store(scout.adapter.MongoAdapter)
        request(flask.request) request sent by browser form to the /panels endpoint

    Returns:
        redirect_id(str): the ID of the panel to redirect the page to
    """
    redirect_id = None
    panel_file = request.files["panel_file"]
    lines = panel_decode_lines(panel_file)

    if not lines:
        return redirect(request.referrer)

    # check if a new panel should be created or the user is modifying an existing one
    if request.form.get("new_panel_name"):  # Create a new panel
        redirect_id = create_new_panel(store, request, lines)
    else:  # Update an existing panel
        redirect_id = update_existing_panel(store, request, lines)

    return redirect_id


def panel(store, panel_obj):
    """Preprocess a panel of genes."""
    panel_obj["institute"] = store.institute(panel_obj["institute"])
    full_name = "{} ({})".format(panel_obj["display_name"], panel_obj["version"])
    panel_obj["name_and_version"] = full_name

    maintainers = panel_obj.get("maintainer") or []

    panel_obj["maintainer_names"] = [
        maintainer_obj.get("name")
        for maintainer_obj in (store.user(user_id=maintainer_id) for maintainer_id in maintainers)
        if maintainer_obj is not None
    ]

    return dict(panel=panel_obj)


def existing_gene(store, panel_obj, hgnc_id):
    """Check if gene is already added to a panel."""
    existing_genes = {gene["hgnc_id"]: gene for gene in panel_obj.get("genes", {})}
    return existing_genes.get(hgnc_id)


def update_panel(store, panel_name, csv_lines, option):
    """Update an existing gene panel with genes.

    Args:
        store(scout.adapter.MongoAdapter)
        panel_name(str)
        csv_lines(iterable(str)): Stream with genes
        option(str): 'add' or 'replace'

    Returns:
        panel_obj(dict)
    """
    new_genes = []
    panel_obj = store.gene_panel(panel_name)
    if panel_obj is None:
        return None

    # retroactively add hidden field
    if not "hidden" in panel_obj:
        panel_obj["hidden"] = False
    try:
        new_genes = parse_genes(csv_lines)  # a list of gene dictionaries containing gene info
    except SyntaxError as error:
        flash(error.args[0], "danger")
        return None

    # if existing genes are to be replaced by those in csv_lines
    if option == "replace":
        # all existing genes should be deleted
        for gene in panel_obj["genes"]:
            # create extra key to use in pending actions:
            gene["hgnc_symbol"] = gene["symbol"]
            store.add_pending(panel_obj, gene, action="delete", info=None)

    for new_gene in new_genes:
        if not new_gene["hgnc_id"]:
            flash("gene missing hgnc id: {}".format(new_gene["hgnc_symbol"]), "danger")
            continue
        gene_obj = store.hgnc_gene_caption(new_gene["hgnc_id"])
        if gene_obj is None:
            flash(
                "gene not found: {} - {}".format(new_gene["hgnc_id"], new_gene["hgnc_symbol"]),
                "danger",
            )
            continue
        if new_gene["hgnc_symbol"] and gene_obj["hgnc_symbol"] != new_gene["hgnc_symbol"]:
            flash(
                "symbol mis-match: {0} | {1}".format(
                    gene_obj["hgnc_symbol"], new_gene["hgnc_symbol"]
                ),
                "warning",
            )

        info_data = {
            "disease_associated_transcripts": new_gene["transcripts"],
            "reduced_penetrance": new_gene["reduced_penetrance"],
            "mosaicism": new_gene["mosaicism"],
            "inheritance_models": new_gene["inheritance_models"],
            "database_entry_version": new_gene["database_entry_version"],
        }
        if (
            option == "replace"
        ):  # there will be no existing genes for sure, because we're replacing them all
            action = "add"
        else:  # add option. Add if genes is not existing. otherwise edit it
            existing_genes = {gene["hgnc_id"] for gene in panel_obj["genes"]}
            action = "edit" if gene_obj["hgnc_id"] in existing_genes else "add"
        store.add_pending(panel_obj, gene_obj, action=action, info=info_data)

    return panel_obj


def new_panel(
    store,
    institute_id,
    panel_name,
    display_name,
    csv_lines,
    maintainer=None,
    description=None,
):
    """Create a new gene panel.

    Args:
        store(scout.adapter.MongoAdapter)
        institute_id(str)
        panel_name(str)
        display_name(str)
        csv_lines(iterable(str)): Stream with genes
        maintainer(list(user._id))
        description(str)

    Returns:
        panel_id: the ID of the new panel document created or None

    """
    institute_obj = store.institute(institute_id)
    if institute_obj is None:
        flash("{}: institute not found".format(institute_id))
        return None

    panel_obj = store.gene_panel(panel_name)
    if panel_obj:
        flash(
            "panel already exists: {} - {}".format(
                panel_obj["panel_name"], panel_obj["display_name"]
            ),
            "danger",
        )
        return None

    LOG.debug("parse genes from CSV input")
    try:
        new_genes = parse_genes(csv_lines)
    except SyntaxError as error:
        flash(error.args[0], "danger")
        LOG.debug("Ooops!")
        return None

    LOG.debug("build new gene panel")

    panel_id = None
    try:
        panel_data = build_panel(
            dict(
                panel_name=panel_name,
                institute=institute_obj["_id"],
                version=1.0,
                maintainer=maintainer,
                date=dt.datetime.now(),
                display_name=display_name,
                description=description,
                genes=new_genes,
                hidden=False,
            ),
            store,
        )
        panel_id = store.add_gene_panel(panel_data)

    except Exception as err:
        flash(str(err), "danger")

    return panel_id


def downloaded_panel_name(panel_obj, format) -> str:
    """Return a string with the file name to be downloaded

    Args:
        panel_obj(dict): scout.models.panel.gene_panel
        format(str): "pdf" or "txt"
    Returns:
        a string describing the panel
    """
    return "_".join(
        [
            panel_obj["panel_name"],
            str(panel_obj["version"]),
            dt.datetime.now().strftime(DATE_DAY_FORMATTER),
            f"scout.{format}",
        ]
    )


def panel_data(store, panel_obj):
    """Preprocess a panel of genes."""
    panel_obj["institute"] = store.institute(panel_obj["institute"])
    full_name = "{}({})".format(panel_obj["display_name"], panel_obj["version"])
    panel_obj["name_and_version"] = full_name

    return dict(panel=panel_obj)


def panel_export_case_hits(panel_id, institute_obj, case_obj):
    """Fetch information required to populate the PDF report containing
    info on actual panel coverage. Currently this is approximated with three parts:
        1) the genes on the panel for SNV and SV
        2) the genes on the panel with any calls reported for STRs
        3) the availability of an SMN Copy Number report if SMN1 or SMN2 is on the gene panel.

    Args:
        panel_id(str): _id of a gene panel
        institute_obj(dict): scout.models.Institute
        case_obj(dict): scout.models.Case

    Returns:
        data(dict): dictionary containing data to be displayed on PDF report
    """
    panel_obj = store.panel(panel_id)
    panel_obj["name_and_version"] = "{}({})".format(panel_obj["display_name"], panel_obj["version"])

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

    data = {"institute": institute_obj, "case": case_obj, "panel": panel_obj, "panel_genes": set()}
    variant_categories = {"str": set(), "smn": set()}
    variants_query = {
        "case_id": case_obj["_id"],
        "category": None,
        "hgnc_ids": None,
    }

    for gene in panel_obj.get("genes", []):
        data["panel_genes"].add(gene["symbol"])
        variants_query["hgnc_ids"] = gene["hgnc_id"]
        for cat, _ in variant_categories.items():
            variants_query["category"] = cat
            res = store.variant_collection.find_one(variants_query)
            if res:
                variant_categories[cat].add(gene["symbol"])

        if gene["symbol"] in ["SMN1", "SMN2"] and case_obj.get("smn_tsv"):
            variant_categories["smn"].add(gene["symbol"])

    data["variant_hits"] = variant_categories

    return data


def get_panels(store, panel_name):
    """Fetch matching gene panels and return a list."""
    gene_panels = list(store.gene_panels(panel_id=panel_name, include_hidden=True))

    return gene_panels
