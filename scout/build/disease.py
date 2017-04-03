import logging

log = logging.getLogger(__name__)

def build_disease_term(disease_info, alias_genes={}):
    """Build a disease phenotype object
    
    Args:
        disease_info(dict): Dictionary with phenotype information
        alias_genes(dict): {
                    <alias_symbol>: {
                                        'true': hgnc_id or None,
                                        'ids': [<hgnc_id>, ...]}}
    
    Returns:
        disease_obj(dict): Formated for mongodb
        
        disease_term = dict(
            _id = str, # Same as disease_id
            disease_id = str, # required, like OMIM:600233
            disase_nr = int, # The disease nr, required
            description = str, # required
            source = str, # required
            inheritance = list, # list of strings
            genes = list, # List with integers that are hgnc_ids 
            hpo_terms = list, # List with str that are hpo_terms 
        )
        
    """
    disease_obj = {}
    
    try:
        disease_nr = int(disease_info['mim_number'])
    except KeyError:
        raise KeyError("Diseases has to have a disease number")
    
    disease_id = "{0}:{1}".format('OMIM', disease_nr)

    disease_obj['_id'] = disease_obj['disease_id'] = disease_id

    log.debug("Building disease term %s", disease_id)

    disease_obj['description'] = disease_info['description']
    
    inheritance_models = disease_info.get('inheritance')
    if inheritance_models:
        disease_obj['inheritance'] = list(inheritance_models)

    hgnc_ids = set()
    for hgnc_symbol in disease_info.get('hgnc_symbols', []):
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

    disease_obj['genes'] = list(hgnc_ids)
    
    if 'hpo_terms' in disease_info:
        disease_obj['hpo_terms'] = list(disease_info['hpo_terms'])
    
    return disease_obj
    