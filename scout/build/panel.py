# -*- coding: utf-8 -*-
import logging

from scout.models.panel import (GenePanel, Gene)

logger = logging.getLogger(__name__)

def build_gene(gene_info):
    """Build a gene panel gene object"""

    gene_obj = Gene(hgnc_id=gene_info['hgnc_id'])
    
    if gene_info.get('hgnc_symbol'):
        gene_obj.symbol = gene_info['hgnc_symbol']

    if gene_info.get('transcripts'):
        gene_obj.disease_associated_transcripts = gene_info['transcripts']
    
    if gene_info.get('reduced_penetrance'):
        gene_obj.reduced_penetrance = True
    
    if gene_info.get('mosaicism'):
        gene_obj.mosaicism = True
    
    if gene_info.get('database_entry_version'):
        gene_obj.database_entry_version = gene_info['database_entry_version']
    
    if gene_info.get('inheritance_models'):
        for model in gene_info['inheritance_models']:
            if model == 'AR':
                gene_obj.ar = True
            if model == 'AD':
                gene_obj.ad = True
            if model == 'MT':
                gene_obj.mt = True
            if model == 'XR':
                gene_obj.xr = True
            if model == 'XD':
                gene_obj.xd = True
            if model == 'X':
                gene_obj.x = True
            if model == 'Y':
                gene_obj.y = True

    return gene_obj


def build_panel(panel_info):
    """Build a mongoengine GenePanel

        Args:
            panel_info(dict): A dictionary with panel information

        Returns:
            panel_obj(GenePanel)

    """
    logger.info("Building panel with id: {0}".format(panel_info['id']))

    panel_obj = GenePanel(
        institute=panel_info['institute'],
        panel_name=panel_info['id'],
        version=panel_info['version'],
        date=panel_info['date'],
    )

    panel_obj.display_name = panel_info['display_name']
    
    gene_objs = []
    for gene_info in panel_info['genes']:
        gene_obj = build_gene(gene_info)
        gene_objs.append(gene_obj)

    panel_obj.genes = gene_objs

    return panel_obj
