# -*- coding: utf-8 -*-
import pytest
from scout.exceptions import IntegrityError

def test_add_disease_term(adapter):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    ## WHEN loading a hpo term
    adapter.load_disease_term(disease_term)

    res = adapter.disease_terms()

    ## THEN assert that the term have been loaded
    assert len([term for term in res]) == 1


def test_add_disease_term(adapter):
    ## GIVEN a empty adapter
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    ## WHEN loading a hpo term twice
    adapter.load_disease_term(disease_term)

    ## THEN IntegrityError should be raised
    with pytest.raises(IntegrityError):
        adapter.load_disease_term(disease_term)


def test_fetch_disease_term(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(disease_term["_id"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == disease_term["_id"]


def test_fetch_disease_term_by_number(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)
    ## WHEN fetching a disease term
    res = adapter.disease_term(disease_term["disease_nr"])

    ## THEN assert the correct term was fetched
    assert res["_id"] == disease_term["_id"]


def test_fetch_disease_term_by_hgnc_id(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)

    disease_term["_id"] = "OMIM:2"
    disease_term["disease_id"] = "OMIM:2"
    disease_term["disease_nr"] = "2"
    adapter.load_disease_term(disease_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=1)

    ## THEN assert the correct term was fetched
    assert len([term for term in res]) == 2


def test_fetch_disease_term_by_hgnc_id_again(adapter):
    ## GIVEN a adapter loaded with one disease term
    assert len([term for term in adapter.disease_terms()]) == 0

    disease_term = dict(
        _id="OMIM:1",
        disease_id="OMIM:1",
        disease_nr=1,
        source="OMIM",
        description="First disease",
        genes=[1],  # List with integers that are hgnc_ids
    )
    adapter.load_disease_term(disease_term)

    disease_term["_id"] = "OMIM:2"
    disease_term["disease_id"] = "OMIM:2"
    disease_term["disease_nr"] = "2"
    disease_term["genes"] = [2]
    adapter.load_disease_term(disease_term)

    ## WHEN fetching a disease term
    res = adapter.disease_terms(hgnc_id=1)

    ## THEN assert the correct term was fetched
    assert len([term for term in res]) == 1
