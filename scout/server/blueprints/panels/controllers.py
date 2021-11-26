# -*- coding: utf-8 -*-
import datetime as dt
import logging
import operator

from flask import abort, flash, redirect, url_for
from flask_login import current_user

from scout.build.panel import build_panel
from scout.parse.panel import parse_genes

log = logging.getLogger(__name__)

INHERITANCE_MODELS = ["ar", "ad", "mt", "xr", "xd", "x", "y"]


def shall_display_panel(panel_obj, user):
    """Check if panel shall be displayed based on display status and user previleges."""
    is_visible = not panel_obj.get("hidden", False)
    return is_visible or panel_write_granted(panel_obj, user)


def panel_write_granted(panel_obj, user):
    return any(
        ["maintainer" not in panel_obj, user.is_admin, user._id in panel_obj.get("maintainer", [])]
    )


def panel_create_or_update(store, request):
    """Process a user request to create a new gene panel

    Args:
        store(scout.adapter.MongoAdapter)
        request(flask.request) request sent by browser form to the /panels endpoint

    """
    # Try to read the csv or txt file containing genes info
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
            "Something went wrong while parsing the panel gene panel file! ({})".format(err),
            "danger",
        )
        return redirect(request.referrer)

    # check if a new panel should be created or the user is modifying an existing one
    new_panel_name = request.form.get("new_panel_name")
    if new_panel_name:  # create a new panel
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
            return redirect(request.referrer)

        flash("new gene panel added, {}!".format(new_panel_name), "success")
        return redirect(url_for("panels.panel", panel_id=new_panel_id))

    # modify an existing panel
    update_option = request.form["modify_option"]

    panel_obj = store.gene_panel(request.form["panel_name"], include_hidden=current_user.is_admin)
    if panel_obj is None:
        return redirect(request.referrer)

    if panel_write_granted(panel_obj, current_user):
        panel_obj = update_panel(
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
        gene_obj = store.hgnc_gene(new_gene["hgnc_id"])
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

    log.debug("parse genes from CSV input")
    try:
        new_genes = parse_genes(csv_lines)
    except SyntaxError as error:
        flash(error.args[0], "danger")
        return None

    log.debug("build new gene panel")

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


def panel_export(store, panel_obj):
    """Preprocess a panel of genes."""
    panel_obj["institute"] = store.institute(panel_obj["institute"])
    full_name = "{}({})".format(panel_obj["display_name"], panel_obj["version"])
    panel_obj["name_and_version"] = full_name

    return dict(panel=panel_obj)
