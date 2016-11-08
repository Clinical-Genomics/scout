# -*- coding: utf-8 -*-
from codecs import open
from scout.models.case.gene_list import Gene

def parse_genes(panel_path, panel_name):
    """Parse a file with genes and return the hgnc ids

    Args:
        panel_path(str): Path to gene panel file
        panel_name(str): Name of the gene panel

    Returns:
        genes(list(str)): List of hgnc ids
    """
    genes = []
    
    header = []

    with open(panel_path, 'r') as f:
        for line in f:
            line = line.rstrip()
            if line.startswith('#'):
                if not line.startswith('##'):
                    header = [word.lower() for word in line[1:].split('\t')]
            else:
                line = line.split('\t')
                gene_info = dict(zip(header, line))
                #These are the panels that the gene belongs to:
                hgnc_symbol = gene_info.get('hgnc_symbol')

                reduced_penetrance = gene_info.get('reduced_penetrance')
                disease_associated_transcripts = gene_info.get('disease_associated_transcripts', '').split(',')
                genetic_disease_models = gene_info.get('genetic_disease_models')
                
                if reduced_penetrance:
                    reduced_penetrance = True
                else:
                    reduced_penetrance = False

                genes.append(hgnc_symbol)
                hgnc_symbols.append(hgnc_symbol)

    return genes


def parse_gene_panel(panel_info, institute):
    """Parse the panel info and return a gene panel

        Args:
            panel_info(dict)
            institute(str)

        Returns:
            gene_panel(dict)
    """

    gene_panel = {}

    gene_panel['path'] = panel_info.get('file')
    gene_panel['institute'] = institute
    gene_panel['type'] = panel_info.get('type', 'clinical')
    gene_panel['date'] = panel_info.get('date')
    gene_panel['version'] = float(panel_info.get('version', '1.0'))
    gene_panel['id'] = panel_info.get('name')
    gene_panel['display_name'] = panel_info.get('full_name', gene_panel['id'])

    gene_panel['genes'] = parse_genes(panel_path=gene_panel['path'],
                                      panel_name=gene_panel['id'])

    return gene_panel
