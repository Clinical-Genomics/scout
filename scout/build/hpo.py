import logging

LOG = logging.getLogger(__name__)

def build_hpo_term(hpo_info):
    """Build a hpo_term object
    
    Check that the information is correct and add the correct hgnc ids to the 
    array of genes.
    
        Args:
            hpo_info(dict)
        
        Returns:
            hpo_obj(dict)
    
        hpo_obj = dict(
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

    LOG.debug("Building hpo term %s", hpo_id)

    # Add description to HPO term
    hpo_obj['description'] = hpo_info.get('description')

    hgnc_ids = hpo_info.get('genes', set())
    
    # Add links to hgnc genes if any
    if hgnc_ids:
        hpo_obj['genes'] = list(hgnc_ids)
    
    return hpo_obj

