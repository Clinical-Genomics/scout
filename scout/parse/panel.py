# -*- coding: utf-8 -*-
from scout.utils.handle import get_file_handle
from scout.models.case.gene_list import Gene

def parse_genes(panel_path):
    """Parse a file with genes and return the hgnc ids

    Args:
        panel_path(str): Path to gene panel file

    Returns:
        genes(list(dict)): Dictionaries with relevant gene info
    """
    genes = []
    header = []

    f = get_file_handle(panel_path)
    for line in f:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = [word.lower() for word in line[1:].split('\t')]
        else:
            line = line.split('\t')
            gene = {}
            gene_info = dict(zip(header, line))
            #These are the panels that the gene belongs to:
            gene['hgnc_id'] = gene_info.get('hgnc_id')
            hgnc_symbol = gene_info.get('hgnc_symbol')
            if hgnc_symbol:
                gene['hgnc_symbol'] = hgnc_symbol.upper()
            else:
                gene['hgnc_symbol'] = None

            transcripts = gene_info.get('disease_associated_transcripts')
            if transcripts:
                gene['disease_associated_transcripts'] = [
                    transcript.split('.')[0] for transcript in transcripts.split(',')
                ]
            else:
                gene['disease_associated_transcripts'] = []
            
            models = gene_info.get('genetic_disease_models')
            if models:
                gene['genetic_disease_models'] = models.split(',')
            else:
                gene['genetic_disease_models'] = []
            
            manual_mosaicism = gene_info.get('mosaicism')
            manual_reduced_penetrance = gene_info.get('reduced_penetrance')
            gene['database_entry_version'] = gene_info.get('database_entry_version')

            gene['mosaicism'] = False
            gene['reduced_penetrance'] = False
            if manual_reduced_penetrance:
                gene['reduced_penetrance'] = True
            if manual_mosaicism:
                gene['mosaicism'] = True

            genes.append(gene)

    return genes


def parse_gene_panel(panel_info):
    """Parse the panel info and return a gene panel

        Args:
            panel_info(dict)

        Returns:
            gene_panel(dict)
    """

    gene_panel = {}

    gene_panel['path'] = panel_info.get('file')
    gene_panel['type'] = panel_info.get('type', 'clinical')
    gene_panel['date'] = panel_info.get('date')
    gene_panel['institute'] = panel_info.get('institute')
    gene_panel['version'] = float(panel_info.get('version', '1.0'))
    gene_panel['id'] = panel_info.get('name')
    gene_panel['display_name'] = panel_info.get('full_name', gene_panel['id'])

    gene_panel['genes'] = parse_genes(panel_path=gene_panel['path'])

    return gene_panel
