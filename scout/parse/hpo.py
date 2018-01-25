import logging

LOG = logging.getLogger(__name__)


def parse_hpo_phenotype(hpo_line):
    """Parse hpo phenotype
    
        Args:
            hpo_line(str): A iterable with hpo phenotype lines
    
        Yields:
            hpo_info(dict)
    """
    hpo_line = hpo_line.rstrip().split('\t')
    hpo_info = {}
    hpo_info['hpo_id'] = hpo_line[0]
    hpo_info['description'] = hpo_line[1]
    hpo_info['hgnc_symbol'] = hpo_line[3]
    
    return hpo_info

def parse_hpo_gene(hpo_line):
    """Parse hpo gene information
    
        Args:
            hpo_line(str): A iterable with hpo phenotype lines
    
        Yields:
            hpo_info(dict)
    """
    if not len(hpo_line) > 3:
        return {}
    hpo_line = hpo_line.rstrip().split('\t')
    hpo_info = {}
    hpo_info['hgnc_symbol'] = hpo_line[1]
    hpo_info['description'] = hpo_line[2]
    hpo_info['hpo_id'] = hpo_line[3]
    
    return hpo_info

def parse_hpo_disease(hpo_line):
    """Parse hpo disease line
    
        Args:
            hpo_line(str)
    """
    hpo_line = hpo_line.rstrip().split('\t')
    hpo_info = {}
    disease = hpo_line[0].split(':')
    
    hpo_info['source'] = disease[0]
    hpo_info['disease_nr'] = int(disease[1])
    hpo_info['hgnc_symbol'] = None
    hpo_info['hpo_term'] = None
    
    if len(hpo_line) >= 3:
        hpo_info['hgnc_symbol'] = hpo_line[2]

        if len(hpo_line) >= 4:
            hpo_info['hpo_term'] = hpo_line[3]
    
    
    return hpo_info

def parse_hpo_phenotypes(hpo_lines):
    """Parse hpo phenotypes
    
        Group the genes that a phenotype is associated to in 'genes'
    
    Args:
        hpo_lines(iterable(str)): A file handle to the hpo phenotypes file
    
    Returns:
        hpo_terms(dict): A dictionary with hpo_ids as keys and terms as values
    
        {
            <hpo_id>: {
                'hpo_id':str,
                'description': str,
                'hgnc_symbols': list(str), # [<hgnc_symbol>, ...]
                }
        }
    """
    hpo_terms = {}
    LOG.info("Parsing hpo phenotypes...")
    for index, line in enumerate(hpo_lines):
        if index > 0 and len(line) > 0:
            hpo_info = parse_hpo_phenotype(line)
            hpo_term = hpo_info['hpo_id']
            hgnc_symbol = hpo_info['hgnc_symbol']
            if hpo_term in hpo_terms:
                hpo_terms[hpo_term]['hgnc_symbols'].append(hgnc_symbol)
            else:
                hpo_terms[hpo_term] = {
                    'hpo_id':hpo_term,
                    'description': hpo_info['description'],
                    'hgnc_symbols': [hgnc_symbol]
                }
    LOG.info("Parsing done.")
    return hpo_terms

def parse_hpo_diseases(hpo_lines):
    """Parse hpo disease phenotypes
    
        Args:
            hpo_lines(iterable(str))
        
        Returns:
            diseases(dict): A dictionary with mim numbers as keys
    """
    diseases = {}
    LOG.info("Parsing hpo diseases...")
    for index, line in enumerate(hpo_lines):
        # First line is a header
        if index == 0:
            continue
        # Skip empty lines
        if not len(line) > 3:
            continue
        # Parse the info
        disease_info = parse_hpo_disease(line)
        # Skip the line if there where no info
        if not disease_info:
            continue
        disease_nr = disease_info['disease_nr']
        hgnc_symbol = disease_info['hgnc_symbol']
        hpo_term = disease_info['hpo_term']
        source = disease_info['source']
        disease_id = "{0}:{1}".format(source, disease_nr)
        
        if disease_id not in diseases:
            diseases[disease_id] = {
                'disease_nr': disease_nr,
                'source': source,
                'hgnc_symbols': set(),
                'hpo_terms': set(),
            }

        if hgnc_symbol:
            diseases[disease_id]['hgnc_symbols'].add(hgnc_symbol)
        if hpo_term:
            diseases[disease_id]['hpo_terms'].add(hpo_term)

    LOG.info("Parsing done.")
    return diseases
    

def parse_hpo_to_genes(hpo_lines):
    """Parse the map from hpo term to hgnc symbol
    
    Args:
        lines(iterable(str)):
    
    Yields:
        hpo_to_gene(dict): A dictionary with information on how a term map to a hgnc symbol
    """
    for line in hpo_lines:
        if line.startswith('#') or len(line) < 1:
            continue
        line = line.rstrip().split('\t')
        hpo_id = line[0]
        hgnc_symbol = line[3]
        
        yield {
            'hpo_id': hpo_id,
            'hgnc_symbol': hgnc_symbol
        }
    
    

def parse_hpo_genes(hpo_lines):
    """Parse HPO gene information
    
        Args:
            hpo_lines(iterable(str))
        
        Returns:
            diseases(dict): A dictionary with hgnc symbols as keys
    """
    LOG.info("Parsing HPO genes ...")
    genes = {}
    for index, line in enumerate(hpo_lines):
        # First line is header
        if index == 0:
            continue
        if len(line) < 5:
            continue
        gene_info = parse_hpo_gene(line)
        hgnc_symbol = gene_info['hgnc_symbol']
        description = gene_info['description']
        
        if hgnc_symbol not in genes:
            genes[hgnc_symbol] = {
                'hgnc_symbol': hgnc_symbol
            }
        
        gene = genes[hgnc_symbol]
        if description == 'Incomplete penetrance':
            gene['incomplete_penetrance'] = True
        if description == 'Autosomal dominant inheritance':
            gene['ad'] = True
        if description == 'Autosomal recessive inheritance':
            gene['ar'] = True
        if description == 'Mithochondrial inheritance':
            gene['mt'] = True
        if description == 'X-linked dominant inheritance':
            gene['xd'] = True
        if description == 'X-linked recessive inheritance':
            gene['xr'] = True
        if description == 'Y-linked inheritance':
            gene['x'] = True
        if description == 'X-linked inheritance':
            gene['y'] = True
    LOG.info("Parsing done.")
    return genes
    

def get_incomplete_penetrance_genes(hpo_lines):
    """Get a set with all genes that have incomplete penetrance according to HPO
    
    Args:
        hpo_lines(iterable(str))
    
    Returns:
        incomplete_penetrance_genes(set): A set with the hgnc symbols of all 
                                          genes with incomplete penetrance
        
    """
    genes = parse_hpo_genes(hpo_lines)
    incomplete_penetrance_genes = set()
    for hgnc_symbol in genes:
        if genes[hgnc_symbol].get('incomplete_penetrance'):
            incomplete_penetrance_genes.add(hgnc_symbol)
    return incomplete_penetrance_genes

def parse_hpo_obo(hpo_lines):
    """Parse a .obo formated hpo line"""
    term = {}
    for line in hpo_lines:
        if len(line) == 0:
            continue
        line = line.rstrip()
        # New term starts with [Term]
        if line == '[Term]':
            if term:
                yield term
            term = {}
        
        elif line.startswith('id'):
            term['hpo_id'] = line[4:]

        elif line.startswith('name'):
            term['description'] = line[6:]

        elif line.startswith('alt_id'):
            if 'aliases' not in term:
                term['aliases'] = []
            term['aliases'].append(line[8:])
        
        elif line.startswith('is_a'):
            if 'ancestors' not in term:
                term['ancestors'] = []
            term['ancestors'].append(line[6:16])

    if term:
        yield term
        

if __name__ == "__main__":
    import sys
    from pprint import pprint as pp
    from scout.utils.handle import get_file_handle
    
    file_handle = get_file_handle(sys.argv[1])
    
    # phenotypes = parse_hpo_phenotypes(file_handle)
    # for hpo_id in phenotypes:
    #     hpo_term = phenotypes[hpo_id]
    #     pp(hpo_term)

    diseases = parse_hpo_diseases(file_handle)
    for mim_id in diseases:
        disease = diseases[mim_id]
        pp(disease)

    # incomplete_genes = get_incomplete_penetrance_genes(file_handle)
    # for gene in incomplete_genes:
    #     print(gene)
    # genes = parse_hpo_genes(file_handle)
    # for hgnc_symbol in genes:
    #     gene = genes[hgnc_symbol]
    #     pp(gene)
