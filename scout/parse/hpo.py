import logging

logger = logging.getLogger(__name__)


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
    logger.info("Parsing hpo phenotypes...")
    for index, line in enumerate(hpo_lines):
        if index > 0:
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
    logger.info("Parsing done.")
    return hpo_terms

def parse_hpo_diseases(hpo_lines):
    """Parse hpo disease phenotypes
    
        Args:
            hpo_lines(iterable(str))
        
        Returns:
            diseases(dict): A dictionary with mim numbers as keys
    """
    diseases = {}
    logger.info("Parsing hpo diseases...")
    for index, line in enumerate(hpo_lines):
        if index > 0:
            disease_info = parse_hpo_disease(line)
            if disease_info:
                disease_nr = disease_info['disease_nr']
                hgnc_symbol = disease_info['hgnc_symbol']
                hpo_term = disease_info['hpo_term']
                source = disease_info['source']
                disease_id = "{0}:{1}".format(source, disease_nr)
                
                if disease_id in diseases:
                    if hgnc_symbol:
                        diseases[disease_id]['hgnc_symbols'].add(hgnc_symbol)
                    if hpo_term:
                        diseases[disease_id]['hpo_terms'].add(hpo_term)
                        
                else:
                    if hgnc_symbol:
                        hgnc_symbols = set([hgnc_symbol])
                    else:
                        hgnc_symbols = set()
                    if hpo_term:
                        hpo_terms = set([hpo_term])
                    else:
                        hpo_terms = set()
                    diseases[disease_id] = {
                        'disease_nr': disease_nr,
                        'source': source,
                        'hgnc_symbols': hgnc_symbols,
                        'hpo_terms': hpo_terms,
                    }

    logger.info("Parsing done.")
    return diseases
    

def parse_hpo_genes(hpo_lines):
    """Parse HPO gene information
    
        Args:
            hpo_lines(iterable(str))
        
        Returns:
            diseases(dict): A dictionary with hgnc symbols as keys
    """
    logger.info("Parsing HPO genes ...")
    genes = {}
    for index, line in enumerate(hpo_lines):
        if index > 0:
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
    logger.info("Parsing done.")
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
