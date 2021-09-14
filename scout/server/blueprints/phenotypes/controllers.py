# -*- coding: utf-8 -*-


def hpo_terms(store, query=None):
    """Retrieves a list of HPO terms from scout database

    Args:
        store (obj): an adapter to the scout database
        query (str): an optional search string requesting the return of only matching HPO terms

    Returns:
        hpo_phenotypes (dict): the complete list of HPO objects stored in scout, or same matching HPO terms

    """
    hpo_phenotypes = {}
    if query:
        hpo_phenotypes["phenotypes"] = list(store.hpo_terms(query=query))
    else:
        hpo_phenotypes["phenotypes"] = list(store.hpo_terms())
    return hpo_phenotypes
