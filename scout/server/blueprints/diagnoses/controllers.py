# -*- coding: utf-8 -*-

def omim_entry(store, omim_id):
    """Retrieve specific info for an OMIM term at the gene level

    Args:
        store(obj): an adapter to the scout database
        omim_id(str): an OMIM _id

    Returns:
        omim_obj(obj): an OMIM term containing description and genes
    """

    omim_obj = store.omim_term(term=omim_id)
    omim_obj['genes_complete'] = store.omim_genes(omim_obj.get('genes',[]))
    omim_obj['hpo_complete'] = [ store.hpo_term(hpo_id) for hpo_id in omim_obj.get('hpo_terms',[])]
    return  omim_obj
