# -*- coding: utf-8 -*-

def hpo_terms(store, query = None, limit = None):
    """Retrieves a list of HPO terms from scout database

    Args:
        store (obj): an adapter to the scout database

    Returns:
        hpo_phenotypes (dict): the complete list of HPO objects stored in scout

    """
    hpo_phenotypes = {}
    if limit:
        limit=int(limit)

    hpo_phenotypes['phenotypes'] = list(store.hpo_terms(query=query,  limit=limit))
    return hpo_phenotypes
