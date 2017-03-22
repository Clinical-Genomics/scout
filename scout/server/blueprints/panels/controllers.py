# -*- coding: utf-8 -*-
import logging

log = logging.getLogger(__name__)

INHERITANCE_MODELS = ['ar', 'ad', 'mt', 'xr', 'xd', 'x', 'y']


def panel(store, panel_id):
    """Preprocess a panel of genes."""
    panel_obj = store.panel(panel_id)
    panel_obj['institute'] = store.institute(panel_obj['institute'])
    full_name = "{} ({})".format(panel_obj['display_name'], panel_obj['version'])
    panel_obj['name_and_version'] = full_name
    return dict(panel=panel_obj)


def existing_gene(store, panel_obj, hgnc_id):
    """Check if gene is already added to a panel."""
    existing_genes = {gene['hgnc_id']: gene for gene in panel_obj['genes']}
    return existing_genes.get(hgnc_id)
