import logging

log = logging.getLogger(__name__)

def build_hpo_term(hpo_info, alias_genes={}):
    """Build a hpo_term object
    
    Check that the information is correct and add the correct hgnc ids to the 
    array of genes.
    
        Args:
            hpo_info(dict)
            alias_genes(dict): {
                    <alias_symbol>: {
                                        'true': hgnc_id or None,
                                        'ids': [<hgnc_id>, ...]}}
    
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

    # Set the id to be the hpo terms id
    hpo_obj['_id'] = hpo_obj['hpo_id'] = hpo_id

    log.debug("Building hpo term %s", hpo_id)

    hpo_obj['description'] = hpo_info.get('description')

    hgnc_ids = set()
    for hgnc_symbol in hpo_info.get('hgnc_symbols', []):
        ## TODO need to consider genome build here?
        if hgnc_symbol in alias_genes:
            # If the symbol identifies a unique gene we add that
            if alias_genes[hgnc_symbol]['true']:
                hgnc_ids.add(alias_genes[hgnc_symbol]['true'])
            else:
                for hgnc_id in alias_genes[hgnc_symbol]['ids']:
                    hgnc_ids.add(hgnc_id)
        else:
            log.debug("Gene symbol %s could not be found in database", hgnc_symbol)
    
    hpo_obj['genes'] = list(hgnc_ids)
    
    return hpo_obj

