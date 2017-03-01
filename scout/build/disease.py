import logging

log = logging.getLogger(__name__)

def build_disease_term(disease_info, adapter):
    """Build a disease phenotype object
    
    Args:
        disease_info(dict): Dictionary with phenotype information
        adapter(scout.adapter.MongoAdapter)
    
    Returns:
        disease_obj(dict): Formated for mongodb
        
        disease_term = dict(
            _id = str, # Same as disease_id
            disease_id = str, # required, like OMIM:600233
            disase_nr = int, # The disease nr, required
            source = str, # required
            inheritance = list, # list of strings
            genes = list, # List with integers that are hgnc_ids 
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

    hgnc_ids = []
    for hgnc_symbol in disease_info.get('hgnc_symbols', []):
        ## TODO need to consider genome build here?
        hgnc_gene = adapter.hgnc_gene(hgnc_symbol)
        if hgnc_gene:
            hgnc_ids.append(hgnc_gene['hgnc_id'])
        else:
            log.warning("Gene %s could not be found in database", hgnc_symbol)
    disease_obj['genes'] = hgnc_ids
    
    return disease_obj
    