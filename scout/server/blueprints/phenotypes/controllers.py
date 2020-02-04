# -*- coding: utf-8 -*-


def hpo_terms(store):
    """Retrieves a list of HPO terms from scout database

    Args:
        store (obj): an adapter to the scout database

    Returns:
        hpo_phenotypes (dict): the complete list of HPO objects stored in scout

    """
    hpo_phenotypes = {}
    hpo_phenotypes["phenotypes"] = list(store.hpo_terms())
    return hpo_phenotypes
