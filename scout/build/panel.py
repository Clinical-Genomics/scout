# -*- coding: utf-8 -*-
import logging

from scout.models.case.gene_list import (GenePanel, Gene)

logger = logging.getLogger(__name__)

def get_hgnc_id(gene_info, adapter):
    """Get the hgnc id for a gene

        The proprity order will be
        1. if there is a hgnc id this one will be choosen
        2. if the hgnc symbol matches a genes proper hgnc symbol
        3. if the symbol ony matches aliases on several genes one will be
           choosen at random

        Args:
            gene_info(dict)
            adapter

        Returns:
            true_id(int)
    """
    hgnc_id = gene_info.get('hgnc_id')
    hgnc_symbol = gene_info.get('hgnc_symbol')

    true_id = None

    if hgnc_id:
        true_id = int(hgnc_id)
    else:
        gene_result = adapter.hgnc_genes(hgnc_symbol)
        if gene_result.count() == 0:
            raise Exception("No gene could be found for {}".format(hgnc_symbol))
        for gene in gene_result:
            if hgnc_symbol.upper() == gene.hgnc_symbol.upper():
                true_id = gene.hgnc_id
        if not gene_info['hgnc_id']:
            true_id = gene.hgnc_id
    return true_id

def build_gene(gene_info, adapter):
    """Build a gene panel gene object"""
    hgnc_id = get_hgnc_id(gene_info, adapter)
    hgnc_gene = adapter.hgnc_gene(hgnc_id)

    gene_obj = Gene(hgnc_gene = hgnc_gene)

    if gene_info['disease_associated_transcripts']:
        gene_obj.disease_associated_transcripts = gene_info['disease_associated_transcripts']
    if gene_info['reduced_penetrance']:
        gene_obj.reduced_penetrance = gene_info['reduced_penetrance']
    if gene_info['mosaicism']:
        gene_obj.mosaicism = gene_info['mosaicism']
    if gene_info['database_entry_version']:
        gene_obj.database_entry_version = gene_info['database_entry_version']

    return gene_obj

def build_panel(panel_info, adapter):
    """Build a mongoengine GenePanel

        Args:
            panel_info(dict): A dictionary with panel information
            adapter(MongoAdapter)

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

    for gene_info in panel_info['genes']:
        hgnc_symbol = gene_info['hgnc_symbol']
        panel_obj.gene_objects[hgnc_symbol] = build_gene(gene_info, adapter)

    return panel_obj
