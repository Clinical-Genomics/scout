# -*- coding: utf-8 -*-

from scout.adapter import MongoAdapter
from scout.server.links import disease_link


def disease_entry(store, disease_id) -> dict:
    """Retrieve specific info for a disease term

    Args:
        store(obj): an adapter to the scout database
        disease_id(str): a disease_id

    Returns:
        disease_obj(obj): a disease term containing description and genes
    """

    disease_obj = store.disease_term(disease_identifier=disease_id, filter_project={})
    disease_obj["genes_complete"] = store.disease_to_genes(disease_obj)
    disease_obj["hpo_complete"] = [
        store.hpo_term(hpo_id) for hpo_id in disease_obj.get("hpo_terms", [])
    ]
    disease_obj["disease_link"] = disease_link(disease_id=disease_obj["disease_id"])
    return disease_obj


def disease_terms(store: MongoAdapter, query: str, source: str) -> dict:
    """Retrieve disease terms, optionally queried by source or a text-match for the disease description."""

    data = {"terms": store.disease_terms(query=query, source=source, filter_project=None)}
    return data
