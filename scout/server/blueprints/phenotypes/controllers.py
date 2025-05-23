# -*- coding: utf-8 -*-

from typing import Optional

from scout.adapter import MongoAdapter
from scout.constants import HPO_LINK_URL


def hpo_terms(
    store: MongoAdapter,
    query: Optional[str] = None,
    limit: Optional[str] = None,
    page: Optional[str] = None,
) -> dict:
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

    data = hpo_phenotypes
    data["hpo_link_url"] = HPO_LINK_URL
    return data
