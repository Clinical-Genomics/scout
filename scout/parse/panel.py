# -*- coding: utf-8 -*-
import logging
from scout.utils.handle import get_file_handle

logger = logging.getLogger(__name__)

VALID_MODELS = ('AR','AD','MT','XD','XR','X','Y')

def parse_gene(gene_line, header):
    """Parse a gene line with information from a panel file
    
        Args:
            gene_line(list[str]): A raw line from the panel file
            header(list[str]): A list with the header information
    
        Returns:
            gene(dict): A dictionary with the gene information
                {
                'hgnc_id': int,
                'hgnc_symbol': str,
                'disease_associated_transcripts': list(str),
                'inheritance_models': list(str),
                'mosaicism': bool,
                'reduced_penetrance': bool,
                'database_entry_version': str,
                }

    """
    gene = {}
    gene_info = dict(zip(header, gene_line))
    
    #The hgnc id allways has to be present
    gene['hgnc_id'] = int(gene_info['hgnc_id'])
    
    #Hgnc symbol is optional
    hgnc_symbol = gene_info.get('hgnc_symbol')
    if hgnc_symbol:
        gene['hgnc_symbol'] = hgnc_symbol.upper()
    else:
        gene['hgnc_symbol'] = None

    # Disease associated transcripts is a ','-separated list of
    # manually curated transcripts 
    transcripts = gene_info.get('disease_associated_transcripts')
    if transcripts:
        gene['transcripts'] = [
            transcript.split('.')[0] for transcript in transcripts.split(',')
        ]
    else:
        gene['transcripts'] = []
    
    # Genetic disease models is a ','-separated list of manually curated
    # inheritance patterns that are followed for a gene
    models = None
    if 'genetic_disease_models' in gene_info:
        models = gene_info.get('genetic_disease_models')
    elif 'inheritance_models' in gene_info:
        models = gene_info.get('inheritance_models')
    elif 'genetic_inheritance_models' in gene_info:
        models = gene_info.get('genetic_inheritance_models')

    gene['inheritance_models'] = []
    if models:
        for model in models.split(','):
            if model in VALID_MODELS:
                gene['inheritance_models'].append(model)
            else:
                logger.warning("Invalid model found in gene %s" % gene['hgnc_id'])
                logger.info("Skipping model %s" % model)
    
    # If a gene is known to be associated with mosaicism this is annotated
    gene['mosaicism'] = True if gene_info.get('mosaicism') else False
    
    # If a gene is known to have reduced penetrance this is annotated
    gene['reduced_penetrance'] = True if gene_info.get('reduced_penetrance') else False
    
    # The database entry version is a way to track when a a gene was added or
    # modified, optional
    gene['database_entry_version'] = gene_info.get('database_entry_version')

    return gene
    

def parse_genes(gene_lines):
    """Parse a file with genes and return the hgnc ids

    Args:
        gene_lines(iterable(str)): Path to gene panel file

    Returns:
        genes(list(dict)): Dictionaries with relevant gene info
    """
    genes = []
    header = []
    hgnc_ids = set()

    for line in gene_lines:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = [word.lower() for word in line[1:].split('\t')]
        else:
            line = line.split('\t')
            gene = parse_gene(line, header)
            
            hgnc_id = gene['hgnc_id']
            
            if not hgnc_id in hgnc_ids:
                hgnc_ids.add(hgnc_id)
                genes.append(gene)

    return genes


def parse_gene_panel(panel_info):
    """Parse the panel info and return a gene panel

        Args:
            panel_info(dict)

        Returns:
            gene_panel(dict)
    """
    logger.info("Parsing gene panel %s" % panel_info.get('panel_name'))
    gene_panel = {}

    gene_panel['path'] = panel_info.get('file')
    gene_panel['type'] = panel_info.get('type', 'clinical')
    gene_panel['date'] = panel_info.get('date')
    gene_panel['institute'] = panel_info.get('institute')
    gene_panel['version'] = float(panel_info.get('version', '1.0'))
    gene_panel['panel_name'] = panel_info.get('panel_name')
    gene_panel['display_name'] = panel_info.get('full_name', gene_panel['panel_name'])

    panel_handle = get_file_handle(gene_panel['path'])
    gene_panel['genes'] = parse_genes(gene_lines=panel_handle)

    return gene_panel
