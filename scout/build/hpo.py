import logging

log = logging.getLogger(__name__)

def build_hpo_term(hpo_info, adapter):
    """Build a hpo_term object
    
    Check that the information is correct and add the correct hgnc ids to the 
    array of genes.
    
        Args:
            hpo_info(dict)
            adapter(scout.adapter.MongoAdapter)
    
        Returns:
            hpo_obj(dict)
    
        hpo_term = dict(
            _id = str, # Same as hpo_id
           hpo_id = str, # Required
           description = str,
           genes = list, # List with integers that are hgnc_ids 
        )
        
    """
    
    hpo_obj = {}
    
    try:
        hpo_id = hpo_info['hpo_id']
    except KeyError:
        raise KeyError("Hpo terms has to have a hpo_id")

    hpo_obj['_id'] = hpo_obj['hpo_id'] = hpo_id

    log.debug("Building hpo term %s", hpo_id)

    hpo_obj['description'] = hpo_info.get('description')

    hgnc_ids = []
    for hgnc_symbol in hpo_info.get('hgnc_symbols', []):
        ## TODO need to consider genome build here?
        hgnc_gene = adapter.hgnc_gene(hgnc_symbol)
        if hgnc_gene:
            hgnc_ids.append(hgnc_gene['hgnc_id'])
        else:
            log.warning("Gene %s could not be found in database", hgnc_symbol)
    hpo_obj['genes'] = hgnc_ids
    
    return hpo_obj

def build_disease_term(disease_info):
    """docstring for build_disease_term"""
    disease_obj = DiseaseTerm(
        disease_id = disease_info['disease_nr'],
        source = disease_info['source'],
    )

    return disease_obj