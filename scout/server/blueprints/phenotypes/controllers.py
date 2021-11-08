# -*- coding: utf-8 -*-


def hpo_terms(store, query=None, limit=None, page=None):
    """Retrieves a list of HPO terms from scout database

    Args:
        store (obj): an adapter to the scout database
        query (str): an optional search string requesting the return of only matching HPO terms
        limit:  max number of phenotypes to return
        page: the page in multiples of limit to return
    Returns:
        hpo_phenotypes (dict): the complete list of HPO objects stored in scout, or same matching HPO terms

    """
    hpo_phenotypes = {}

    skip = None
    if limit:
        limit = int(limit)

    if page and limit:
        page = int(page)
        if page > 0:
            skip = (page - 1) * limit
        else:
            skip = 0
    if query:
        hpo_phenotypes["phenotypes"] = list(store.hpo_terms(query=query, limit=limit, skip=skip))
    else:
        hpo_phenotypes["phenotypes"] = list(store.hpo_terms(limit=limit, skip=skip))
    return hpo_phenotypes
