# -*- coding: utf-8 -*-


def omim_entry(store, omim_nr):
    """Retrieve specific info for an OMIM term at the gene level

    Args:
        store(obj): an adapter to the scout database
        omim_nr(str): an OMIM disease_nr

    Returns:
        omim_obj(obj): an OMIM term containing description and genes
    """

    omim_obj = store.disease_term(disease_identifier=omim_nr)
    omim_obj["genes_complete"] = store.omim_to_genes(omim_obj)
    omim_obj["hpo_complete"] = [store.hpo_term(hpo_id) for hpo_id in omim_obj.get("hpo_terms", [])]
    return omim_obj


def disease_terms(store):
    """Retrieve all disease terms.
    Args:
        store(adapter.MongoAdapter):  an adapter to the scout database
    Returns:
        data(dict): dict with key "terms" set to an array of all disease terms
    """

    data = {"terms": store.disease_terms()}
    return data
