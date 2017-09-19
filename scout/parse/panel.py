# -*- coding: utf-8 -*-
import logging
from scout.utils.handle import get_file_handle

logger = logging.getLogger(__name__)

VALID_MODELS = ('AR','AD','MT','XD','XR','X','Y')

def parse_gene(gene_info):
    """Parse a gene line with information from a panel file

        Args:
            gene_info(dict): dictionary with gene info

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
    # This is either hgnc id or hgnc symbol
    identifier = None

    hgnc_id = None
    try:
        if 'hgnc_id' in gene_info:
            hgnc_id = int(gene_info['hgnc_id'])
        elif 'hgnc_idnumber' in gene_info:
            hgnc_id = int(gene_info['hgnc_idnumber'])
        elif 'hgncid' in gene_info:
            hgnc_id = int(gene_info['hgncid'])
    except ValueError as e:
        raise SyntaxError("Invalid hgnc id: {0}".format(hgnc_id))

    gene['hgnc_id'] = hgnc_id
    identifier = hgnc_id

    hgnc_symbol = None
    if 'hgnc_symbol' in gene_info:
        hgnc_symbol = gene_info['hgnc_symbol']
    elif 'hgncsymbol' in gene_info:
        hgnc_symbol = gene_info['hgncsymbol']
    elif 'symbol' in gene_info:
        hgnc_symbol = gene_info['symbol']

    gene['hgnc_symbol'] = hgnc_symbol

    if not identifier:
        if hgnc_symbol:
            identifier = hgnc_symbol
        else:
            raise SyntaxError("No gene identifier could be found")
    gene['identifier'] = identifier
    # Disease associated transcripts is a ','-separated list of
    # manually curated transcripts
    transcripts = ""
    if 'disease_associated_transcripts' in gene_info:
        transcripts = gene_info['disease_associated_transcripts']
    elif 'disease_associated_transcript' in gene_info:
        transcripts = gene_info['disease_associated_transcript']
    elif 'transcripts' in gene_info:
        transcripts = gene_info['transcripts']

    gene['transcripts'] = [
            transcript.strip() for transcript in
            transcripts.split(',') if transcript
        ]

    # Genetic disease models is a ','-separated list of manually curated
    # inheritance patterns that are followed for a gene
    models = ""
    if 'genetic_disease_models' in gene_info:
        models = gene_info['genetic_disease_models']
    elif 'genetic_disease_model' in gene_info:
        models = gene_info['genetic_disease_model']
    elif 'inheritance_models' in gene_info:
        models = gene_info['inheritance_models']
    elif 'genetic_inheritance_models' in gene_info:
        models = gene_info['genetic_inheritance_models']

    gene['inheritance_models'] = [
        model.strip() for model in models.split(',')
        if model.strip() in VALID_MODELS
    ]

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
        gene_lines(iterable(str)): Stream with genes

    Returns:
        genes(list(dict)): Dictionaries with relevant gene info
    """
    genes = []
    header = []
    hgnc_identifiers = set()
    # This can be '\t' or ';'
    delimiter = '\t'

    # There are files that have '#' to indicate headers
    # There are some files that start with a header line without
    # any special symbol
    for i,line in enumerate(gene_lines):
        line = line.rstrip()
        if not len(line) > 0:
            continue
        if line.startswith('#'):
            if not line.startswith('##'):
                if ';' in line:
                    delimiter = ';'
                header = [word.lower() for word in line[1:].split(delimiter)]
        else:
            # If no header symbol assume first line is header
            if i == 0:
                # Check the delimiter
                if ';' in line:
                    delimiter = ';'
                # If first line is a header 'hgnc' should be there
                if ('hgnc' in line or 'HGNC' in line):
                    header = [word.lower() for word in line.split(delimiter)]
                    continue
                else:
                # If first line is not a header try to sniff what the first
                # columns holds
                    if line.split(delimiter)[0].isdigit():
                        header = ['hgnc_id']
                    else:
                        header = ['hgnc_symbol']

            splitted_line = line.split(delimiter)
            gene_info = dict(zip(header, splitted_line))

            # There are cases when excel exports empty lines that looks like
            # ;;;;;;;. This is a exception to handle these
            info_found = False
            for key in gene_info:
                if gene_info[key]:
                    info_found = True
                    break
            # If no info was found we skip that line
            if not info_found:
                continue

            try:
                gene = parse_gene(gene_info)
            except Exception as e:
                logger.warning(e)
                raise SyntaxError("Line {0} is malformed".format(i))

            identifier = gene.pop('identifier')

            if not identifier in hgnc_identifiers:
                hgnc_identifiers.add(identifier)
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
