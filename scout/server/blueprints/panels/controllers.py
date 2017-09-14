# -*- coding: utf-8 -*-
import logging

from flask import flash

from scout.server.userpanel import parse_panel

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
    existing_genes = {gene['hgnc_id'] for gene in panel_obj['genes']}
    new_genes = parse_panel(csv_lines)
    for new_gene in new_genes:
        gene_obj = store.hgnc_gene(new_gene['hgnc_id'])
        if gene_obj is None:
            flash("gene not found: {} - {}".format(new_gene['hgnc_id'], new_gene['symbol']),
                  'danger')
            continue
        if new_gene['symbol'] and gene_obj['hgnc_symbol'] != new_gene['symbol']:
            flash("symbol mis-match: {} | {}".format(gene_obj['hgnc_symbol'], new_gene['symbol']),
                  'warning')
        action = 'edit' if gene_obj['hgnc_id'] in existing_genes else 'add'
        info_data = {
            'disease_associated_transcripts': new_gene['disease_associated_transcripts'],
            'reduced_penetrance': new_gene['reduced_penetrance'],
            'mosaicism': new_gene['mosaicism'],
            'inheritance_models': new_gene['inheritance_models'],
            'database_entry_version': new_gene['database_entry_version'],
        }
        store.add_pending(panel_obj, gene_obj['hgnc_id'], action=action, info=info_data)
    return panel_obj
