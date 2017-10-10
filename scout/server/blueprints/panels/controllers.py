# -*- coding: utf-8 -*-
import datetime as dt
import logging

from flask import flash

from scout.parse.panel import parse_genes
from scout.build.panel import build_panel

log = logging.getLogger(__name__)

INHERITANCE_MODELS = ['ar', 'ad', 'mt', 'xr', 'xd', 'x', 'y']


def panel(store, panel_obj):
    """Preprocess a panel of genes."""
    panel_obj['institute'] = store.institute(panel_obj['institute'])
    full_name = "{} ({})".format(panel_obj['display_name'], panel_obj['version'])
    panel_obj['name_and_version'] = full_name
    return dict(panel=panel_obj)


def existing_gene(store, panel_obj, hgnc_id):
    """Check if gene is already added to a panel."""
    existing_genes = {gene['hgnc_id']: gene for gene in panel_obj['genes']}
    return existing_genes.get(hgnc_id)


def update_panel(store, panel_name, csv_lines):
    """Update an existing gene panel with genes."""
    panel_obj = store.gene_panel(panel_name)
    if panel_obj is None:
        return None

    existing_genes = {gene['hgnc_id'] for gene in panel_obj['genes']}
    try:
        new_genes = parse_genes(csv_lines)
    except SyntaxError as error:
        flash(error.args[0], 'danger')
        return None

    for new_gene in new_genes:
        if not new_gene['hgnc_id']:
            flash("gene missing hgnc id: {}".format(new_gene['hgnc_symbol']),
                  'danger')
            continue

        gene_obj = store.hgnc_gene(new_gene['hgnc_id'])
        if gene_obj is None:
            flash("gene not found: {} - {}".format(new_gene['hgnc_id'], new_gene['hgnc_symbol']),
                  'danger')
            continue
        if new_gene['hgnc_symbol'] and gene_obj['hgnc_symbol'] != new_gene['hgnc_symbol']:
            flash("symbol mis-match: {} | {}".format(gene_obj['hgnc_symbol'],
                  new_gene['hgnc_symbol']), 'warning')
        action = 'edit' if gene_obj['hgnc_id'] in existing_genes else 'add'
        info_data = {
            'disease_associated_transcripts': new_gene['transcripts'],
            'reduced_penetrance': new_gene['reduced_penetrance'],
            'mosaicism': new_gene['mosaicism'],
            'inheritance_models': new_gene['inheritance_models'],
            'database_entry_version': new_gene['database_entry_version'],
        }
        store.add_pending(panel_obj, gene_obj, action=action, info=info_data)
    return panel_obj


def new_panel(store, institute_id, panel_name, display_name, csv_lines):
    """Create a new gene panel."""
    institute_obj = store.institute(institute_id)
    if institute_obj is None:
        flash("{}: institute not found".format(institute_id))
        return None

    panel_obj = store.gene_panel(panel_name)
    if panel_obj:
        flash("panel already exists: {} - {}".format(panel_obj['panel_name'],
                                                     panel_obj['display_name']))
        return None

    log.debug("parse genes from CSV input")
    try:
        new_genes = parse_genes(csv_lines)
    except SyntaxError as error:
        flash(error.args[0], 'danger')
        return None

    log.debug("build new gene panel")
    panel_data = build_panel(dict(
        panel_name=panel_name,
        institute=institute_obj['_id'],
        version=1.0,
        date=dt.datetime.now(),
        display_name=display_name,
        genes=new_genes,
    ), store)

    panel_obj = store.add_gene_panel(panel_data)
    return panel_obj
