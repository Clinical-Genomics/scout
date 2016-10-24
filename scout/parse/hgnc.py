import logging

logger = logging.getLogger(__name__)

# def parse_hgnc_genes(lines):
#     """Read the genes from a hgnc file and create objects for hgnc map"""
#     header = []
#     for index, line in enumerate(lines):
#         line = line.rstrip().split('\t')
#         if index == 0:
#             header = line
#         else:
#             hgnc_gene = {}
#             aliases = []
#             raw_info = dict(zip(header, line))
#             if not 'Withdrawn' in raw_info['status']:
#                 hgnc_symbol = raw_info['symbol']
#                 hgnc_gene['hgnc_symbol'] = hgnc_symbol
#                 aliases.append(hgnc_symbol)
#
#                 previous_names = raw_info['prev_symbol'].strip('"')
#                 if previous_names:
#                     for alias in previous_names.split('|'):
#                         aliases.append(alias)
#                 hgnc_gene['aliases'] = aliases
#
#                 yield hgnc_gene

def parse_hgnc_line(line, header):
    """Parse an hgnc formated line
    
        Args:
            line(list): A list with hgnc gene info
            header(list): A list with the header info
        
        Returns:
            hgnc_info(dict): A dictionary with the relevant info
    """
    hgnc_gene = {}
    raw_info = dict(zip(header, line))
    if not 'Withdrawn' in raw_info['status']:
        hgnc_symbol = raw_info['symbol']
        hgnc_gene['hgnc_symbol'] = hgnc_symbol
        hgnc_gene['hgnc_id'] = int(raw_info['hgnc_id'].split(':')[-1])
        hgnc_gene['description'] = raw_info['name']
        # We want to have the current symbol as an alias
        aliases = [hgnc_symbol]
        previous_names = raw_info['prev_symbol']
        if previous_names:
            aliases += previous_names.split('|')
        
        hgnc_gene['previous'] = aliases
        
        omim_id = raw_info.get('omim_id')
        if omim_id:
            hgnc_gene['omim_ids'] = omim_id.strip('"').split('|')
        else:
            hgnc_gene['omim_ids'] = None
        
        entrez_id = hgnc_gene['entrez_id'] = raw_info.get('entrez_id')
        if entrez_id:
            hgnc_gene['entrez_id'] = int(entrez_id)
        else:
            hgnc_gene['entrez_id'] = None
        
        hgnc_gene['ref_seq'] = raw_info.get('refseq_accession')
        
        uniprot_ids = raw_info.get('uniprot_ids')
        if uniprot_ids:
            hgnc_gene['uniprot_ids'] = uniprot_ids.split('|')
        else:
            hgnc_gene['uniprot_ids'] = None
        
        ucsc_id = raw_info.get('ucsc_id')
        if ucsc_id:
            hgnc_gene['ucsc_id'] = ucsc_id
        else:
            hgnc_gene['ucsc_id'] = None

        vega_id = raw_info.get('vega_id')
        if vega_id:
            hgnc_gene['vega_id'] = vega_id
        else:
            hgnc_gene['vega_id'] = None

    return hgnc_gene
    

def parse_hgnc_genes(lines):
    """Parse lines with hgnc formated genes
        
        This is designed to take a dump with genes from HGNC.
        This is downloaded from: 
        ftp://ftp.ebi.ac.uk/pub/databases/genenames/new/tsv/hgnc_complete_set.txt
    
        Args:
            lines(iterable(str)): An iterable with HGNC formated genes
        Yields:
            hgnc_gene(dict): A dictionary with the relevant information
    """
    header = []
    logger.info("Parsing hgnc genes...")
    for index, line in enumerate(lines):
        line = line.rstrip().split('\t')
        if index == 0:
            header = line
        else:
            
            hgnc_gene = parse_hgnc_line(line=line, header=header)
            if hgnc_gene:
                yield hgnc_gene
